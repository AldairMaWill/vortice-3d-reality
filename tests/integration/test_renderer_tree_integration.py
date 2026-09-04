"""
Test de integración: crea un HolographicWidget real (requiere una
plataforma Qt, aunque sea 'offscreen') y comprueba que el árbol de
cubos que expone coincide con el que gestiona CubeTreeManager, y que
seleccionar un cubo desde el widget se refleja correctamente.

Se salta automáticamente si no hay entorno gráfico disponible ni
siquiera en modo offscreen (por ejemplo, algunos runners de CI sin
las librerías X11/EGL necesarias para PyOpenGL/PyQt5).
"""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pyqt5 = pytest.importorskip("PyQt5.QtWidgets")


@pytest.fixture(scope="module")
def qapp():
    from PyQt5.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def test_holographic_widget_exposes_tree_manager_state(qapp):
    from src.render.renderer import HolographicWidget

    widget = HolographicWidget()
    assert widget.root_cube is not None
    assert len(widget.cubes) == 4

    next_cube = widget.tree.select_next_cube()
    assert widget.selected_cube_index == widget.cubes.index(next_cube)


def test_add_image_to_selected_cube_fills_a_face(qapp):
    import numpy as np
    from src.render.renderer import HolographicWidget

    widget = HolographicWidget()
    fake_image = np.zeros((32, 32, 3), dtype=np.uint8)

    ok = widget.add_image_to_selected_cube(fake_image, "test.png")
    assert ok is True

    selected = widget.get_selected_cube()
    assert any(img is not None for img in selected.face_images)
