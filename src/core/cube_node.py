"""
core/cube_node.py
Representa un cubo individual dentro del árbol jerárquico. Extraído 1:1
de la clase `CubeNode` del monolito original.
"""

from src.utils.config import FACE_NAMES


class CubeNode:
    """Representa un cubo individual en el árbol."""

    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.children = []
        self.images = []  # Imágenes en las caras del cubo
        self.position = (0, 0, 0)  # Posición en el espacio 3D
        self.size = 1.2
        self.is_visible = True
        self.is_selected = False
        self.level = 0  # Nivel en el árbol (0 = raíz)

        # Color del cubo (para identificación)
        self.color = (0.0, 0.8, 0.8)

        # Datos de OpenGL (se llenan al renderizar)
        self.texture_ids = [None] * 6  # Una textura por cara
        self.face_images = [None] * 6  # Imagen por cara
        self.face_names = list(FACE_NAMES)

    def add_child(self, child):
        child.parent = self
        child.level = self.level + 1
        self.children.append(child)
        return child

    def add_image_to_face(self, face_index, image, name="Imagen"):
        """Añade una imagen a una cara específica (0-5)."""
        if 0 <= face_index < 6:
            self.face_images[face_index] = image
            self.images.append((face_index, image, name))
            return True
        return False

    def get_next_empty_face(self):
        """Obtiene el índice de la siguiente cara vacía."""
        for i in range(6):
            if self.face_images[i] is None:
                return i
        return -1
