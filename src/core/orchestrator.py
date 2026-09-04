"""
core/orchestrator.py
Ventana principal ("Cerebro Central"): construye la UI, conecta los
botones de gestión de cubos con CubeTreeManager, carga imágenes en el
HolographicWidget y alimenta las barras de progreso con ProcessSimulator.
Extraído de la clase `PrometeoOctacoreWindow` del monolito original,
delegando ahora en los módulos separados en vez de tener toda la lógica
en un único archivo.
"""

import cv2
import numpy as np
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QGroupBox, QTreeWidget, QTreeWidgetItem, QProgressBar,
    QMessageBox, QInputDialog, QFileDialog,
)
from PyQt5.QtGui import QColor

from src.core.multiprocessing import ProcessSimulator
from src.render.renderer import HolographicWidget
from src.utils.config import (
    WINDOW_TITLE, WINDOW_GEOMETRY, LEFT_PANEL_WIDTH, RIGHT_PANEL_WIDTH,
    STYLESHEET, BACKGROUND_PRESETS, BG_BLACK, BG_DARK_BLUE, BG_HOLOGREEN,
    BRAIN_UPDATE_INTERVAL_MS,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PrometeoOctacoreWindow(QMainWindow):
    """Interfaz principal con biblioteca de cubos en árbol."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(*WINDOW_GEOMETRY)
        self.setStyleSheet(STYLESHEET)

        self.process_simulator = ProcessSimulator()

        self.setup_ui()

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.parallel_processing_simulation)
        self.update_timer.start(BRAIN_UPDATE_INTERVAL_MS)

        self.holographic_widget.cubeSelected.connect(self.on_cube_selected)

    # ------------------------------------------------------------------
    # Construcción de la UI
    # ------------------------------------------------------------------
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        left_panel = self._build_left_panel()
        self.holographic_widget = HolographicWidget()
        self.holographic_widget.rotationChanged.connect(self.update_camera_spins)
        self.holographic_widget.zoomChanged.connect(self.update_camera_zoom_slider)
        right_panel = self._build_right_panel()

        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.holographic_widget, 1)
        main_layout.addWidget(right_panel)

        self.update_tree()
        self.update_info()

    def _build_left_panel(self):
        left_panel = QWidget()
        left_panel.setFixedWidth(LEFT_PANEL_WIDTH)
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        title = QLabel("🔮 PROMETEO-OCTACORE")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title)

        # Fondos degradados
        bg_group = QGroupBox("🌈 FONDOS DEGRADADOS")
        bg_layout = QVBoxLayout()
        bg_type_layout = QHBoxLayout()
        bg_type_layout.addWidget(QLabel("Tipo:"))
        self.bg_type_combo = QComboBox()
        self.bg_type_combo.addItems(BACKGROUND_PRESETS)
        self.bg_type_combo.currentIndexChanged.connect(self.change_background_type)
        bg_type_layout.addWidget(self.bg_type_combo)
        bg_layout.addLayout(bg_type_layout)
        bg_group.setLayout(bg_layout)
        left_layout.addWidget(bg_group)

        # Gestión de cubos
        cube_group = QGroupBox("📦 GESTIÓN DE CUBOS")
        cube_layout = QVBoxLayout()

        btn_add_cube = QPushButton("➕ Añadir Cubo Hijo")
        btn_add_cube.clicked.connect(self.add_child_cube)
        cube_layout.addWidget(btn_add_cube)

        btn_add_sibling = QPushButton("➕ Añadir Cubo Hermano")
        btn_add_sibling.clicked.connect(self.add_sibling_cube)
        cube_layout.addWidget(btn_add_sibling)

        btn_delete_cube = QPushButton("🗑️ Eliminar Cubo")
        btn_delete_cube.clicked.connect(self.delete_selected_cube)
        cube_layout.addWidget(btn_delete_cube)

        btn_rename_cube = QPushButton("✏️ Renombrar Cubo")
        btn_rename_cube.clicked.connect(self.rename_selected_cube)
        cube_layout.addWidget(btn_rename_cube)

        cube_group.setLayout(cube_layout)
        left_layout.addWidget(cube_group)

        # Carga de imágenes
        load_group = QGroupBox("📂 CARGAR IMAGEN AL CUBO")
        load_layout = QVBoxLayout()

        btn_load = QPushButton("📤 Cargar Imagen al Cubo Seleccionado")
        btn_load.clicked.connect(self.load_image_to_selected_cube)
        load_layout.addWidget(btn_load)

        btn_load_multi = QPushButton("📤 Cargar Múltiples al Cubo")
        btn_load_multi.clicked.connect(self.load_multiple_to_selected_cube)
        load_layout.addWidget(btn_load_multi)

        load_group.setLayout(load_layout)
        left_layout.addWidget(load_group)

        # Árbol de cubos
        tree_group = QGroupBox("🌳 ÁRBOL DE CUBOS")
        tree_layout = QVBoxLayout()

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Cubos")
        self.tree_widget.itemClicked.connect(self.select_cube_from_tree)
        tree_layout.addWidget(self.tree_widget)

        tree_group.setLayout(tree_layout)
        left_layout.addWidget(tree_group)

        left_layout.addStretch()
        return left_panel

    def _build_right_panel(self):
        right_panel = QWidget()
        right_panel.setFixedWidth(RIGHT_PANEL_WIDTH)
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        info_group = QGroupBox("📊 INFORMACIÓN")
        info_layout = QVBoxLayout()
        self.info_text = QLabel("Sistema listo\n\nCubos: 0\nCubo seleccionado: Ninguno\nFPS: 60")
        self.info_text.setStyleSheet("font-family: 'Courier New'; font-size: 11px; padding: 5px;")
        self.info_text.setWordWrap(True)
        info_layout.addWidget(self.info_text)
        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)

        proc_group = QGroupBox("⚡ PROCESAMIENTO")
        proc_layout = QVBoxLayout()
        self.progress_bars = []
        for i in range(self.process_simulator.num_brains):
            bar_label = QLabel(f"Cerebro {i + 1}")
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setStyleSheet(
                "QProgressBar { border: 1px solid #ffdd00; } "
                "QProgressBar::chunk { background: #00ddff; }"
            )
            proc_layout.addWidget(bar_label)
            proc_layout.addWidget(bar)
            self.progress_bars.append(bar)
        proc_group.setLayout(proc_layout)
        right_layout.addWidget(proc_group)

        shortcuts_group = QGroupBox("⌨️ ATAJOS")
        shortcuts_layout = QVBoxLayout()
        shortcuts_layout.addWidget(QLabel("Espacio: Siguiente cubo"))
        shortcuts_layout.addWidget(QLabel("R: Reset vista"))
        shortcuts_layout.addWidget(QLabel("Flechas: Mover cámara"))
        shortcuts_layout.addWidget(QLabel("G: Grid"))
        shortcuts_layout.addWidget(QLabel("E: Bordes cubos"))
        shortcuts_group.setLayout(shortcuts_layout)
        right_layout.addWidget(shortcuts_group)

        right_layout.addStretch()
        return right_panel

    # ------------------------------------------------------------------
    # Fondo
    # ------------------------------------------------------------------
    def change_background_type(self, index):
        bg_type = self.bg_type_combo.currentText()

        if bg_type == "Sólido (Negro)":
            self.holographic_widget.set_solid_color(BG_BLACK)
        elif bg_type == "Sólido (Azul Noche)":
            self.holographic_widget.set_solid_color(BG_DARK_BLUE)
        elif bg_type == "Sólido (Verde Holográfico)":
            self.holographic_widget.set_solid_color(BG_HOLOGREEN)
        elif bg_type == "Degradado Radial":
            self.holographic_widget.set_gradient('radial', BG_DARK_BLUE, BG_BLACK)
        elif bg_type == "Degradado Lineal":
            self.holographic_widget.set_gradient('linear', BG_DARK_BLUE, BG_BLACK)
        elif bg_type == "Estrella (Starburst)":
            self.holographic_widget.set_gradient('starburst', BG_DARK_BLUE, BG_BLACK, BG_HOLOGREEN)
        elif bg_type == "Nebulosa":
            self.holographic_widget.set_gradient('nebula', BG_DARK_BLUE, BG_BLACK)

        self.update_info()

    # ------------------------------------------------------------------
    # Gestión de cubos
    # ------------------------------------------------------------------
    def add_child_cube(self):
        selected = self.holographic_widget.get_selected_cube()
        if selected is None:
            QMessageBox.warning(self, "Error", "Selecciona un cubo primero")
            return

        name, ok = QInputDialog.getText(self, "Nuevo Cubo", "Nombre del cubo:")
        if ok and name:
            cube = self.holographic_widget.tree.create_child_cube_with_layout(selected, name)
            self.holographic_widget.tree.select_cube(cube)
            self.update_tree()
            self.update_info()
            self.holographic_widget.updateGL()

    def add_sibling_cube(self):
        selected = self.holographic_widget.get_selected_cube()
        if selected is None or selected.parent is None:
            QMessageBox.warning(self, "Error", "Selecciona un cubo con padre")
            return

        name, ok = QInputDialog.getText(self, "Nuevo Cubo Hermano", "Nombre del cubo:")
        if ok and name:
            cube = self.holographic_widget.tree.create_sibling_cube_with_layout(selected, name)
            self.holographic_widget.tree.select_cube(cube)
            self.update_tree()
            self.update_info()
            self.holographic_widget.updateGL()

    def delete_selected_cube(self):
        selected = self.holographic_widget.get_selected_cube()
        if selected is None:
            QMessageBox.warning(self, "Error", "Selecciona un cubo primero")
            return

        if selected == self.holographic_widget.root_cube:
            QMessageBox.warning(self, "Error", "No puedes eliminar el cubo raíz")
            return

        reply = QMessageBox.question(
            self, 'Confirmar',
            f'¿Eliminar el cubo "{selected.name}" y todos sus hijos?',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.holographic_widget.tree.delete_cube(selected)
            self.update_tree()
            self.update_info()
            self.holographic_widget.updateGL()

    def rename_selected_cube(self):
        selected = self.holographic_widget.get_selected_cube()
        if selected is None:
            QMessageBox.warning(self, "Error", "Selecciona un cubo primero")
            return

        name, ok = QInputDialog.getText(self, "Renombrar Cubo", "Nuevo nombre:", text=selected.name)
        if ok and name:
            self.holographic_widget.tree.rename_cube(selected, name)
            self.update_tree()
            self.update_info()

    def select_cube_from_tree(self, item, column):
        cube_name = item.text(0)
        cube = self.holographic_widget.get_cube_by_name(cube_name)
        if cube:
            self.holographic_widget.tree.select_cube(cube)
            self.holographic_widget.updateGL()
            self.update_info()

    def on_cube_selected(self, index):
        self.update_info()
        self.update_tree()

    # ------------------------------------------------------------------
    # Carga de imágenes
    # ------------------------------------------------------------------
    def load_image_to_selected_cube(self):
        selected = self.holographic_widget.get_selected_cube()
        if selected is None:
            QMessageBox.warning(self, "Error", "Selecciona un cubo primero")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Cargar Imagen al Cubo", "", "Imágenes (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        if file_path:
            image = cv2.imread(file_path)
            if image is not None:
                success = self.holographic_widget.add_image_to_selected_cube(
                    image, file_path.split('/')[-1]
                )
                if success:
                    self.update_info()
                    self.holographic_widget.updateGL()
                else:
                    QMessageBox.warning(self, "Error", "El cubo ya tiene 6 caras llenas")

    def load_multiple_to_selected_cube(self):
        selected = self.holographic_widget.get_selected_cube()
        if selected is None:
            QMessageBox.warning(self, "Error", "Selecciona un cubo primero")
            return

        files, _ = QFileDialog.getOpenFileNames(
            self, "Cargar Múltiples Imágenes", "", "Imágenes (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        if files:
            for file_path in files:
                image = cv2.imread(file_path)
                if image is not None:
                    success = self.holographic_widget.add_image_to_selected_cube(
                        image, file_path.split('/')[-1]
                    )
                    if not success:
                        break
            self.update_info()
            self.holographic_widget.updateGL()

    # ------------------------------------------------------------------
    # Actualización de UI
    # ------------------------------------------------------------------
    def update_tree(self):
        self.tree_widget.clear()
        if self.holographic_widget.root_cube:
            self.add_tree_item(self.tree_widget, self.holographic_widget.root_cube, None)

    def add_tree_item(self, parent_widget, cube, parent_item):
        if parent_item is None:
            item = QTreeWidgetItem(parent_widget)
        else:
            item = QTreeWidgetItem(parent_item)

        item.setText(0, cube.name)

        if cube == self.holographic_widget.get_selected_cube():
            font = item.font(0)
            font.setBold(True)
            item.setFont(0, font)
            item.setForeground(0, QColor(0, 255, 136))

        item.setData(0, Qt.UserRole, cube)

        for child in cube.children:
            self.add_tree_item(None, child, item)

        if parent_item is not None:
            parent_item.addChild(item)

    def update_info(self):
        selected = self.holographic_widget.get_selected_cube()
        selected_name = selected.name if selected else "Ninguno"

        status = "Sistema: ACTIVO\n"
        status += f"Cubos: {len(self.holographic_widget.cubes)}\n"
        status += f"Seleccionado: {selected_name}\n"
        status += f"Nivel: {selected.level if selected else 0}\n"
        status += (
            f"Caras ocupadas: "
            f"{sum(1 for img in selected.face_images if img is not None) if selected else 0}/6\n"
        )
        status += f"FPS: {np.random.randint(55, 65)}"

        self.info_text.setText(status)

    # ------------------------------------------------------------------
    # Cámara (slots de compatibilidad con las señales del renderer)
    # ------------------------------------------------------------------
    def update_camera_spins(self, x, y, z):
        pass

    def update_camera_zoom_slider(self, zoom):
        pass

    def reset_camera_view(self):
        self.holographic_widget.camera.reset()
        self.holographic_widget.updateGL()

    # ------------------------------------------------------------------
    # Simulación de procesamiento en paralelo
    # ------------------------------------------------------------------
    def parallel_processing_simulation(self):
        values = self.process_simulator.tick()
        for bar, value in zip(self.progress_bars, values):
            bar.setValue(value)
