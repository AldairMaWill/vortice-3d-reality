"""
main.py
Punto de entrada de VORTICE
Ejecuta: `python main.py` desde la raíz del proyecto.
"""

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from src.core.orchestrator import PrometeoOctacoreWindow


def main():
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = PrometeoOctacoreWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
