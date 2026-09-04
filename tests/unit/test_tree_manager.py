from src.core.tree_manager import CubeTreeManager


def test_init_tree_creates_root_and_three_children():
    tree = CubeTreeManager()
    assert tree.root_cube.name == "Biblioteca Principal"
    assert len(tree.cubes) == 4  # raíz + 3 hijos de ejemplo


def test_create_child_cube_with_layout_appends_to_parent():
    tree = CubeTreeManager()
    root = tree.root_cube
    child = tree.create_child_cube_with_layout(root, "Nuevo Cubo")
    assert child in root.children
    assert child in tree.cubes
    assert child.level == root.level + 1


def test_delete_cube_removes_from_tree():
    tree = CubeTreeManager()
    target = tree.cubes[1]
    parent = target.parent
    assert tree.delete_cube(target) is True
    assert target not in tree.cubes
    assert target not in parent.children


def test_cannot_delete_root_cube():
    tree = CubeTreeManager()
    assert tree.delete_cube(tree.root_cube) is False
    assert tree.root_cube in tree.cubes


def test_select_next_cube_cycles_through_all():
    tree = CubeTreeManager()
    seen = set()
    for _ in range(len(tree.cubes)):
        seen.add(tree.select_next_cube().name)
    assert len(seen) == len(tree.cubes)
