"""
utils/config.py
Configuración central: constantes de ventana, colores, espaciado del árbol
y flags de entorno. Sustituye a los "números mágicos" que estaban dispersos
por todo el monolito original.
"""

import os

# ---------------------------------------------------------------------------
# Ventana principal
# ---------------------------------------------------------------------------
WINDOW_TITLE = "PROMETEO-OCTACORE - Biblioteca de Cubos en Árbol"
WINDOW_GEOMETRY = (100, 100, 1500, 850)

LEFT_PANEL_WIDTH = 340
RIGHT_PANEL_WIDTH = 250

# ---------------------------------------------------------------------------
# Cámara / vista 3D
# ---------------------------------------------------------------------------
DEFAULT_ZOOM = -12.0
MIN_ZOOM = -30.0
MAX_ZOOM = -2.0
ZOOM_STEP = 0.5
ROTATION_SENSITIVITY = 0.5
TRANSLATION_SENSITIVITY = 0.01
KEYBOARD_PAN_STEP = 0.1

# ---------------------------------------------------------------------------
# Árbol de cubos
# ---------------------------------------------------------------------------
TREE_SPACING_X = 2.5
TREE_SPACING_Y = 2.5
TREE_SPACING_Z = 2.5

ROOT_CUBE_SIZE = 1.2
CHILD_CUBE_SIZE = 0.8
CHILD_SIZE_LEVEL_INCREMENT = 0.1

LEVEL_COLORS = [
    (0.0, 0.8, 0.8),   # nivel 0 - cian
    (0.0, 0.8, 0.5),   # nivel 1 - verde azulado
    (0.5, 0.8, 0.0),   # nivel 2 - verde lima
    (0.8, 0.5, 0.0),   # nivel 3 - naranja
]

FACE_NAMES = ['Frontal', 'Trasera', 'Izquierda', 'Derecha', 'Superior', 'Inferior']

# ---------------------------------------------------------------------------
# Fondos degradados
# ---------------------------------------------------------------------------
BG_WIDTH = 1024
BG_HEIGHT = 768

BG_BLACK = (0.0, 0.0, 0.0)
BG_DARK_BLUE = (0.02, 0.02, 0.06)
BG_HOLOGREEN = (0.0, 0.03, 0.0)

BACKGROUND_PRESETS = [
    "Sólido (Negro)",
    "Sólido (Azul Noche)",
    "Sólido (Verde Holográfico)",
    "Degradado Radial",
    "Degradado Lineal",
    "Estrella (Starburst)",
    "Nebulosa",
]

# ---------------------------------------------------------------------------
# Simulación de procesamiento paralelo ("8 cerebros")
# ---------------------------------------------------------------------------
NUM_SIMULATED_BRAINS = 8
BRAIN_UPDATE_INTERVAL_MS = 100

# ---------------------------------------------------------------------------
# Estilo Qt (hoja de estilos holográfica)
# ---------------------------------------------------------------------------
STYLESHEET = """
    QMainWindow { background-color: #0a0a0f; }
    QLabel, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox, QListWidget, QLineEdit, QTreeWidget {
        color: #ffdd00;
        background-color: #1a1a2e;
        border: 1px solid #ffdd00;
        border-radius: 5px;
        padding: 5px;
        font-family: 'Courier New', monospace;
    }
    QPushButton:hover {
        background-color: #ffdd00;
        color: #0a0a0f;
    }
    QGroupBox {
        border: 2px solid #ffdd00;
        border-radius: 8px;
        margin-top: 10px;
        color: #ffdd00;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
    }
    QSlider::groove:horizontal {
        border: 1px solid #ffdd00;
        height: 8px;
        background: #1a1a2e;
        border-radius: 4px;
    }
    QSlider::handle:horizontal {
        background: #ffdd00;
        border: 1px solid #ffdd00;
        width: 18px;
        margin: -5px 0;
        border-radius: 9px;
    }
    QListWidget {
        background-color: #0a0a0f;
        color: #ffdd00;
        border: 1px solid #ffdd00;
    }
    QListWidget::item:selected {
        background-color: #ffdd00;
        color: #0a0a0f;
    }
    QTreeWidget {
        background-color: #0a0a0f;
        color: #ffdd00;
        border: 1px solid #ffdd00;
    }
    QTreeWidget::item:selected {
        background-color: #ffdd00;
        color: #0a0a0f;
    }
"""

# ---------------------------------------------------------------------------
# Variables de entorno (ver .env.example)
# ---------------------------------------------------------------------------
LOG_LEVEL = os.getenv("VORTICE_LOG_LEVEL", "INFO")
ENABLE_GESTURE_TRACKING = os.getenv("VORTICE_ENABLE_GESTURES", "false").lower() == "true"
