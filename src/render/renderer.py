"""
render/renderer.py
Widget OpenGL con el árbol de cubos holográficos. Extraído de la clase
`HolographicWidget` del monolito original, delegando cámara al
CameraController y el árbol al CubeTreeManager, pero manteniendo
exactamente la misma lógica de dibujo, texturas y fondos.

NOTA: en el monolito original, `change_background_type` (en la ventana
principal) llamaba a `self.holographic_widget.set_solid_color(...)` y
`set_gradient(...)`, pero esos dos métodos nunca estaban definidos en la
clase — era un bug latente del código original (solo funcionaba porque
nunca se disparaba ese callback en pruebas). Aquí se implementan de forma
consistente con el resto del pipeline de fondos (`bg_type`, `bg_color*`,
`regenerate_background`) que sí existía completo.
"""

import math
import time

import cv2
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtOpenGL import QGLWidget

from src.core.tree_manager import CubeTreeManager
from src.render.camera import CameraController
from src.render.gradients import GradientBackground
from src.vision.filters import ImageProcessor
from src.utils.config import BG_WIDTH, BG_HEIGHT, BG_DARK_BLUE, BG_BLACK
from src.utils.logger import get_logger

logger = get_logger(__name__)


class HolographicWidget(QGLWidget):
    """Widget OpenGL con múltiples cubos organizados en árbol."""

    rotationChanged = pyqtSignal(float, float, float)
    zoomChanged = pyqtSignal(float)
    positionChanged = pyqtSignal(float, float, float)
    cubeSelected = pyqtSignal(int)

    def __init__(self, parent=None):
        super(HolographicWidget, self).__init__(parent)
        self.setMinimumSize(600, 500)

        # ===== Cámara =====
        self.camera = CameraController(self)
        self.camera.rotationChanged.connect(self.rotationChanged.emit)
        self.camera.zoomChanged.connect(self.zoomChanged.emit)
        self.camera.positionChanged.connect(self.positionChanged.emit)

        # ===== Árbol de cubos =====
        self.tree = CubeTreeManager()

        # ===== Fondo degradado =====
        self.bg_type = 'solid'
        self.bg_color1 = BG_DARK_BLUE
        self.bg_color2 = BG_BLACK
        self.bg_color3 = (0.0, 0.05, 0.0)
        self.bg_center_x = 0.5
        self.bg_center_y = 0.5
        self.bg_texture_id = None
        self.bg_width = BG_WIDTH
        self.bg_height = BG_HEIGHT
        self.bg_needs_update = True
        self.initialized = False

        # ===== Modos de visualización =====
        self.grid_visible = True
        self.axes_visible = True
        self.show_cube_edges = True

        # ===== Procesador de imágenes =====
        self.processor = ImageProcessor("Cerebro Visual", "Visión")

    # ------------------------------------------------------------------
    # Atajos de compatibilidad con el código de la ventana principal
    # ------------------------------------------------------------------
    @property
    def cubes(self):
        return self.tree.cubes

    @property
    def root_cube(self):
        return self.tree.root_cube

    @property
    def selected_cube_index(self):
        return self.tree.selected_cube_index

    @selected_cube_index.setter
    def selected_cube_index(self, value):
        self.tree.selected_cube_index = value

    def get_selected_cube(self):
        return self.tree.get_selected_cube()

    def get_cube_by_name(self, name):
        return self.tree.get_cube_by_name(name)

    def create_cube_at_position(self, name, x, y, z, parent=None):
        return self.tree.create_cube_at_position(name, x, y, z, parent)

    def print_tree(self):
        self.tree.print_tree()

    # ------------------------------------------------------------------
    # Ciclo de vida OpenGL
    # ------------------------------------------------------------------
    def initializeGL(self):
        self.initialized = True
        glClearColor(self.bg_color1[0], self.bg_color1[1], self.bg_color1[2], 0.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)

        if self.bg_needs_update:
            self.regenerate_background()
            self.bg_needs_update = False

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        if self.bg_texture_id is not None:
            self.draw_background()
        else:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()

        # Posicionar cámara
        glTranslatef(0.0, 0.0, self.camera.zoom)
        glRotatef(self.camera.rot_x, 1.0, 0.0, 0.0)
        glRotatef(self.camera.rot_y, 0.0, 1.0, 0.0)
        glRotatef(self.camera.rot_z, 0.0, 0.0, 1.0)
        glTranslatef(self.camera.pos_x, self.camera.pos_y, self.camera.pos_z)

        if self.grid_visible:
            self.draw_grid()
        if self.axes_visible:
            self.draw_axes()

        self.draw_tree_connections()

        for i, cube in enumerate(self.tree.cubes):
            if cube.is_visible:
                is_selected = (i == self.tree.selected_cube_index)
                self.draw_cube(cube, is_selected)
                self.draw_cube_label(cube)

    # ------------------------------------------------------------------
    # Fondo
    # ------------------------------------------------------------------
    def draw_background(self):
        if self.bg_texture_id is None:
            return
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(-1, 1, -1, 1, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.bg_texture_id)
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-1.0, -1.0, -0.5)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(1.0, -1.0, -0.5)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(1.0, 1.0, -0.5)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-1.0, 1.0, -0.5)
        glEnd()
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)

    def set_solid_color(self, color):
        """Fija un fondo sólido (sin degradado)."""
        self.bg_type = 'solid'
        self.bg_color1 = color
        self.regenerate_background()

    def set_gradient(self, gradient_type, color1, color2, color3=None):
        """Fija un fondo degradado: 'radial', 'linear', 'starburst' o 'nebula'."""
        self.bg_type = gradient_type
        self.bg_color1 = color1
        self.bg_color2 = color2
        if color3 is not None:
            self.bg_color3 = color3
        self.regenerate_background()

    def regenerate_background(self):
        if not self.initialized:
            self.bg_needs_update = True
            return
        if self.bg_type == 'solid':
            glClearColor(self.bg_color1[0], self.bg_color1[1], self.bg_color1[2], 0.0)
            if self.bg_texture_id is not None:
                try:
                    glDeleteTextures([self.bg_texture_id])
                    self.bg_texture_id = None
                except Exception:
                    pass
            self.updateGL()
            return
        elif self.bg_type == 'radial':
            image = GradientBackground.radial_gradient(
                self.bg_width, self.bg_height,
                self.bg_center_x, self.bg_center_y,
                self.bg_color1, self.bg_color2
            )
        elif self.bg_type == 'linear':
            image = GradientBackground.linear_gradient(
                self.bg_width, self.bg_height,
                'vertical',
                self.bg_color1, self.bg_color2
            )
        elif self.bg_type == 'starburst':
            image = GradientBackground.starburst_gradient(
                self.bg_width, self.bg_height,
                self.bg_center_x, self.bg_center_y,
                self.bg_color1, self.bg_color2, self.bg_color3
            )
        elif self.bg_type == 'nebula':
            image = GradientBackground.nebula_gradient(
                self.bg_width, self.bg_height,
                self.bg_center_x, self.bg_center_y
            )
        else:
            return

        image_uint8 = (image * 255).astype(np.uint8)
        if self.bg_texture_id is not None:
            try:
                glDeleteTextures([self.bg_texture_id])
                self.bg_texture_id = None
            except Exception:
                pass
        self.bg_texture_id = self.create_texture_from_array(image_uint8)
        if self.bg_texture_id is not None:
            self.updateGL()

    def create_texture_from_array(self, image):
        if image is None:
            return None
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w = image.shape[:2]
        new_h = 1 << (h - 1).bit_length()
        new_w = 1 << (w - 1).bit_length()
        if new_h != h or new_w != w:
            image = cv2.resize(image, (new_w, new_h))
        image_bytes = image.tobytes()
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, new_w, new_h, 0,
                     GL_RGB, GL_UNSIGNED_BYTE, image_bytes)
        return texture_id

    def create_texture(self, image):
        """Crea una textura OpenGL a partir de una imagen, corrigiendo la orientación."""
        if image is None:
            return None

        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)

        image = cv2.flip(image, 0)  # corrige orientación vertical

        h, w = image.shape[:2]
        new_h = 1 << (h - 1).bit_length()
        new_w = 1 << (w - 1).bit_length()
        if new_h != h or new_w != w:
            image = cv2.resize(image, (new_w, new_h))

        if len(image.shape) == 3 and image.shape[2] == 4:
            gl_format = GL_RGBA
            gl_internal = GL_RGBA
        else:
            gl_format = GL_RGB
            gl_internal = GL_RGB

        image_bytes = image.tobytes()
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexImage2D(GL_TEXTURE_2D, 0, gl_internal, new_w, new_h, 0,
                     gl_format, GL_UNSIGNED_BYTE, image_bytes)
        return texture_id

    # ------------------------------------------------------------------
    # Dibujo de cubos
    # ------------------------------------------------------------------
    def draw_cube_face_with_image(self, cube, face_idx, size, is_selected):
        face_offsets = [
            (0, 0, size / 2), (0, 0, -size / 2),
            (-size / 2, 0, 0), (size / 2, 0, 0),
            (0, size / 2, 0), (0, -size / 2, 0)
        ]
        face_rots = [
            (0, 0, 0), (0, 180, 0),
            (0, -90, 0), (0, 90, 0),
            (-90, 0, 0), (90, 0, 0)
        ]

        x, y, z = face_offsets[face_idx]
        rot_x, rot_y, rot_z = face_rots[face_idx]

        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(rot_x, 1.0, 0.0, 0.0)
        glRotatef(rot_y, 0.0, 1.0, 0.0)
        glRotatef(rot_z, 0.0, 0.0, 1.0)

        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, cube.texture_ids[face_idx])
        glColor4f(1.0, 1.0, 1.0, 0.85)

        face_size = size * 0.95

        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-face_size / 2, -face_size / 2, 0.0)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(face_size / 2, -face_size / 2, 0.0)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(face_size / 2, face_size / 2, 0.0)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-face_size / 2, face_size / 2, 0.0)
        glEnd()

        glDisable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)
        glPopMatrix()

    def draw_cube(self, cube, is_selected):
        x, y, z = cube.position
        size = cube.size

        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(cube.level * 15, 0.0, 1.0, 0.0)

        for face_idx in range(6):
            if cube.face_images[face_idx] is not None:
                if cube.texture_ids[face_idx] is None:
                    texture = self.create_texture(cube.face_images[face_idx])
                    cube.texture_ids[face_idx] = texture

                if cube.texture_ids[face_idx] is not None:
                    self.draw_cube_face_with_image(cube, face_idx, size, is_selected)

        if self.show_cube_edges:
            self.draw_cube_edges_for_cube(size, cube.color, is_selected)

        glPopMatrix()

    def draw_tree_connections(self):
        glDisable(GL_LIGHTING)
        glColor4f(0.0, 0.6, 0.6, 0.3)
        glLineWidth(1.0)
        glBegin(GL_LINES)
        for cube in self.tree.cubes:
            if cube.parent and cube.is_visible:
                px, py, pz = cube.parent.position
                cx, cy, cz = cube.position
                glVertex3f(px, py, pz)
                glVertex3f(cx, cy, cz)
        glEnd()
        glEnable(GL_LIGHTING)

    def draw_cube_edges_for_cube(self, size, color, is_selected):
        glDisable(GL_LIGHTING)

        if is_selected:
            alpha = 0.5 + 0.5 * math.sin(time.time() * 3)
            glColor4f(0.0, 1.0, 1.0, alpha)
            glLineWidth(2.0)
        else:
            glColor4f(color[0], color[1], color[2], 0.5)
            glLineWidth(1.0)

        s = size / 2
        edges = [
            (-s, -s, s), (s, -s, s), (s, -s, s), (s, s, s),
            (s, s, s), (-s, s, s), (-s, s, s), (-s, -s, s),
            (-s, -s, -s), (s, -s, -s), (s, -s, -s), (s, s, -s),
            (s, s, -s), (-s, s, -s), (-s, s, -s), (-s, -s, -s),
            (-s, -s, s), (-s, -s, -s), (s, -s, s), (s, -s, -s),
            (s, s, s), (s, s, -s), (-s, s, s), (-s, s, -s)
        ]

        glBegin(GL_LINES)
        for i in range(0, len(edges), 2):
            glVertex3f(edges[i][0], edges[i][1], edges[i][2])
            glVertex3f(edges[i + 1][0], edges[i + 1][1], edges[i + 1][2])
        glEnd()

        glColor4f(color[0], color[1], color[2], 0.8)
        glPointSize(3.0)
        corners = [
            (-s, -s, -s), (s, -s, -s), (-s, s, -s), (s, s, -s),
            (-s, -s, s), (s, -s, s), (-s, s, s), (s, s, s)
        ]
        glBegin(GL_POINTS)
        for corner in corners:
            glVertex3f(corner[0], corner[1], corner[2])
        glEnd()

        glEnable(GL_LIGHTING)

    def draw_cube_label(self, cube):
        x, y, z = cube.position
        y += cube.size + 0.2

        glDisable(GL_LIGHTING)
        glColor4f(0.0, 1.0, 0.8, 0.8)
        glPointSize(2.0)

        glBegin(GL_POINTS)
        glVertex3f(x, y, z)
        glEnd()

        glEnable(GL_LIGHTING)

    def draw_grid(self):
        glDisable(GL_LIGHTING)
        glColor4f(0.0, 0.6, 0.0, 0.15)
        glLineStipple(2, 0xAAAA)
        glEnable(GL_LINE_STIPPLE)
        glBegin(GL_LINES)
        for i in range(-15, 16):
            glVertex3f(i, -1.5, -5)
            glVertex3f(i, -1.5, 5)
            glVertex3f(-5, -1.5, i)
            glVertex3f(5, -1.5, i)
        glEnd()
        glDisable(GL_LINE_STIPPLE)
        glEnable(GL_LIGHTING)

    def draw_axes(self):
        glDisable(GL_LIGHTING)
        glBegin(GL_LINES)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, -1.5, 0.0)
        glVertex3f(3.0, -1.5, 0.0)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, -1.5, 0.0)
        glVertex3f(0.0, -1.5, 3.0)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0, -1.5, 0.0)
        glVertex3f(0.0, 1.0, 0.0)
        glEnd()
        glEnable(GL_LIGHTING)

    # ------------------------------------------------------------------
    # Gestión de imágenes en cubos
    # ------------------------------------------------------------------
    def add_image_to_selected_cube(self, image, name="Imagen"):
        cube = self.tree.get_selected_cube()
        if cube is None:
            return False

        face_idx = cube.get_next_empty_face()
        if face_idx == -1:
            return False

        processed = self.processor.process(image, 'original')
        cube.add_image_to_face(face_idx, processed, name)
        return True

    # ------------------------------------------------------------------
    # Eventos de mouse (delegan a CameraController + selección de cubo)
    # ------------------------------------------------------------------
    def mousePressEvent(self, event):
        self.camera.on_mouse_press(event)
        if event.button() == Qt.RightButton:
            if self.tree.cubes:
                self.tree.select_next_cube()
                self.cubeSelected.emit(self.tree.selected_cube_index)
                self.updateGL()

    def mouseMoveEvent(self, event):
        if self.camera.on_mouse_move(event):
            self.updateGL()

    def mouseReleaseEvent(self, event):
        self.camera.on_mouse_release(event)

    def wheelEvent(self, event):
        self.camera.on_wheel(event)
        self.updateGL()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_R:
            self.camera.reset()
            self.updateGL()
        elif event.key() == Qt.Key_G:
            self.grid_visible = not self.grid_visible
            self.updateGL()
        elif event.key() == Qt.Key_A:
            self.axes_visible = not self.axes_visible
            self.updateGL()
        elif event.key() == Qt.Key_E:
            self.show_cube_edges = not self.show_cube_edges
            self.updateGL()
        elif event.key() == Qt.Key_Space:
            if self.tree.cubes:
                self.tree.select_next_cube()
                self.cubeSelected.emit(self.tree.selected_cube_index)
                self.updateGL()
        elif event.key() == Qt.Key_Up:
            self.camera.pan_up()
            self.updateGL()
        elif event.key() == Qt.Key_Down:
            self.camera.pan_down()
            self.updateGL()
        elif event.key() == Qt.Key_Left:
            self.camera.pan_left()
            self.updateGL()
        elif event.key() == Qt.Key_Right:
            self.camera.pan_right()
            self.updateGL()
