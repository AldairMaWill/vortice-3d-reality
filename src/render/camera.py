"""
render/camera.py
Controlador de cámara (órbita con mouse, zoom con rueda, paneo con
teclado/mouse). Extrae la lógica de cámara que en el monolito original
vivía mezclada dentro de HolographicWidget.mousePressEvent /
mouseMoveEvent / wheelEvent / keyPressEvent, sin cambiar ninguna
sensibilidad ni límite numérico.
"""

from PyQt5.QtCore import QObject, QPoint, pyqtSignal

from src.utils.config import (
    DEFAULT_ZOOM, MIN_ZOOM, MAX_ZOOM, ZOOM_STEP,
    ROTATION_SENSITIVITY, TRANSLATION_SENSITIVITY, KEYBOARD_PAN_STEP,
)


class CameraController(QObject):
    """Encapsula el estado y la lógica de la cámara orbital."""

    rotationChanged = pyqtSignal(float, float, float)
    zoomChanged = pyqtSignal(float)
    positionChanged = pyqtSignal(float, float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rot_x = 0.0
        self.rot_y = 0.0
        self.rot_z = 0.0
        self.zoom = DEFAULT_ZOOM
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.pos_z = 0.0

        self.last_pos = QPoint()
        self.rotation_mode = False
        self.translation_mode = False

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------
    def reset(self):
        self.rot_x = 0.0
        self.rot_y = 0.0
        self.rot_z = 0.0
        self.zoom = DEFAULT_ZOOM
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.pos_z = 0.0

    # ------------------------------------------------------------------
    # Eventos de mouse
    # ------------------------------------------------------------------
    def on_mouse_press(self, event):
        from PyQt5.QtCore import Qt

        self.last_pos = event.pos()
        if event.button() == Qt.LeftButton:
            self.rotation_mode = True
        elif event.button() == Qt.MiddleButton:
            self.translation_mode = True

    def on_mouse_move(self, event):
        """Devuelve True si el estado cambió y hace falta redibujar."""
        dx = event.x() - self.last_pos.x()
        dy = event.y() - self.last_pos.y()

        if self.rotation_mode:
            self.rot_y += dx * ROTATION_SENSITIVITY
            self.rot_x += dy * ROTATION_SENSITIVITY
            self.last_pos = event.pos()
            self.rotationChanged.emit(self.rot_x, self.rot_y, self.rot_z)
            return True
        elif self.translation_mode:
            self.pos_x += dx * TRANSLATION_SENSITIVITY
            self.pos_y -= dy * TRANSLATION_SENSITIVITY
            self.last_pos = event.pos()
            self.positionChanged.emit(self.pos_x, self.pos_y, self.pos_z)
            return True
        return False

    def on_mouse_release(self, event):
        self.rotation_mode = False
        self.translation_mode = False

    def on_wheel(self, event):
        delta = event.angleDelta().y() / 120
        self.zoom += delta * ZOOM_STEP
        self.zoom = max(MIN_ZOOM, min(MAX_ZOOM, self.zoom))
        self.zoomChanged.emit(self.zoom)

    # ------------------------------------------------------------------
    # Paneo por teclado (flechas)
    # ------------------------------------------------------------------
    def pan_up(self):
        self.pos_y += KEYBOARD_PAN_STEP

    def pan_down(self):
        self.pos_y -= KEYBOARD_PAN_STEP

    def pan_left(self):
        self.pos_x -= KEYBOARD_PAN_STEP

    def pan_right(self):
        self.pos_x += KEYBOARD_PAN_STEP
