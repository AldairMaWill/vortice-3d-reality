"""
core/tree_manager.py
Gestión del árbol jerárquico de cubos, separada del widget OpenGL para
que el "Cerebro Central" (orchestrator) y el renderer compartan la misma
fuente de verdad. La lógica (posiciones, colores por nivel, layout en
abanico al añadir hijos/hermanos) es la misma que tenía el monolito
original, solo que ahora vive en un único lugar en vez de repartida
entre HolographicWidget y PrometeoOctacoreWindow.
"""

import math

from src.core.cube_node import CubeNode
from src.utils.config import LEVEL_COLORS, CHILD_CUBE_SIZE, CHILD_SIZE_LEVEL_INCREMENT
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CubeTreeManager:
    """Mantiene el árbol de cubos y las operaciones de alto nivel sobre él."""

    def __init__(self):
        self.root_cube = None
        self.cubes = []  # Lista plana de todos los cubos
        self.selected_cube_index = -1
        self.init_tree()

    # ------------------------------------------------------------------
    # Inicialización
    # ------------------------------------------------------------------
    def init_tree(self):
        """Inicializa el árbol con un cubo raíz y tres hijos de ejemplo."""
        root = CubeNode("Biblioteca Principal")
        root.position = (0, 0, 0)
        root.level = 0
        root.color = LEVEL_COLORS[0]
        self.root_cube = root
        self.cubes = [root]

        self.add_cube_to_parent(root, "Proyectos", (-2.5, 0, 0))
        self.add_cube_to_parent(root, "Recursos", (2.5, 0, 0))
        self.add_cube_to_parent(root, "Referencias", (0, 0, -2.5))

        self.selected_cube_index = 0
        logger.info("Árbol inicializado con %d cubos", len(self.cubes))

    # ------------------------------------------------------------------
    # Creación de cubos
    # ------------------------------------------------------------------
    def add_cube_to_parent(self, parent, name, position):
        """Añade un cubo hijo a un padre, en una posición explícita."""
        cube = CubeNode(name, parent)
        cube.position = position
        cube.level = parent.level + 1
        cube.size = CHILD_CUBE_SIZE
        cube.color = LEVEL_COLORS[min(cube.level, len(LEVEL_COLORS) - 1)]

        parent.add_child(cube)
        self.cubes.append(cube)
        return cube

    def create_cube_at_position(self, name, x, y, z, parent=None):
        """Crea un cubo en una posición específica del espacio 3D."""
        if parent is None:
            parent = self.root_cube

        cube = CubeNode(name, parent)
        cube.position = (x, y, z)
        cube.level = parent.level + 1
        cube.size = CHILD_CUBE_SIZE + (CHILD_SIZE_LEVEL_INCREMENT * cube.level)
        cube.color = LEVEL_COLORS[min(cube.level, len(LEVEL_COLORS) - 1)]

        parent.add_child(cube)
        self.cubes.append(cube)
        return cube

    def create_child_cube_with_layout(self, parent, name):
        """Calcula automáticamente una posición en abanico para un hijo nuevo."""
        children_count = len(parent.children)
        angle = children_count * 1.2
        radius = 2.0 + parent.level * 0.5

        x = parent.position[0] + radius * math.cos(angle)
        z = parent.position[2] + radius * math.sin(angle)
        y = parent.position[1] - 0.5

        return self.create_cube_at_position(name, x, y, z, parent)

    def create_sibling_cube_with_layout(self, sibling, name):
        """Crea un hermano de `sibling`, reutilizando el layout en abanico del padre."""
        if sibling.parent is None:
            return None
        return self.create_child_cube_with_layout(sibling.parent, name)

    # ------------------------------------------------------------------
    # Borrado / renombrado
    # ------------------------------------------------------------------
    def delete_cube(self, cube):
        """Elimina un cubo (no la raíz) del árbol y de la lista plana."""
        if cube is None or cube is self.root_cube:
            return False
        if cube.parent:
            cube.parent.children.remove(cube)
        if cube in self.cubes:
            self.cubes.remove(cube)
        self.selected_cube_index = 0
        return True

    def rename_cube(self, cube, new_name):
        if cube is None or not new_name:
            return False
        cube.name = new_name
        return True

    # ------------------------------------------------------------------
    # Selección / búsqueda
    # ------------------------------------------------------------------
    def get_selected_cube(self):
        if 0 <= self.selected_cube_index < len(self.cubes):
            return self.cubes[self.selected_cube_index]
        return None

    def select_next_cube(self):
        if self.cubes:
            self.selected_cube_index = (self.selected_cube_index + 1) % len(self.cubes)
        return self.get_selected_cube()

    def select_cube(self, cube):
        if cube in self.cubes:
            self.selected_cube_index = self.cubes.index(cube)
            return True
        return False

    def get_cube_by_name(self, name):
        for cube in self.cubes:
            if cube.name == name:
                return cube
        return None

    # ------------------------------------------------------------------
    # Debug / introspección
    # ------------------------------------------------------------------
    def print_tree(self):
        """Imprime el árbol en consola (debug)."""

        def print_node(cube, indent=""):
            print(f"{indent}├── {cube.name} (nivel {cube.level})")
            for child in cube.children:
                print_node(child, indent + "│   ")

        if self.root_cube:
            print_node(self.root_cube)
