"""
vision/tracker.py

AVISO IMPORTANTE:
El monolito original que compartiste NO incluía tracking de manos/gestos
con MediaPipe: toda la cámara y selección de cubos se controlaba con
mouse y teclado (ver src/render/camera.py). Este módulo es un STUB
deshabilitado por defecto para no inventar funcionalidad que no existía.

Está aquí para que el proyecto respete la estructura de carpetas pedida
(docs/GESTURE_CONTROLS.md) y puedas activarlo en el futuro sin tocar el
resto de la arquitectura: solo tendrías que implementar `read_frame()` y
conectar `GestureTracker.get_gesture()` a HolographicWidget.

Actívalo con VORTICE_ENABLE_GESTURES=true en tu .env, pero no hará nada
hasta que implementes la lógica de MediaPipe aquí dentro.
"""

from src.utils.config import ENABLE_GESTURE_TRACKING
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GestureTracker:
    """Placeholder para integración futura con MediaPipe Hands.

    No se activa ni se importa mediapipe a menos que
    ENABLE_GESTURE_TRACKING sea True, para no añadir una dependencia
    pesada que el proyecto original no usaba.
    """

    def __init__(self):
        self.enabled = ENABLE_GESTURE_TRACKING
        self._hands = None

        if self.enabled:
            try:
                import mediapipe as mp  # noqa: F401  (import diferido a propósito)
                logger.info("GestureTracker: mediapipe detectado, listo para implementar.")
            except ImportError:
                logger.warning(
                    "VORTICE_ENABLE_GESTURES=true pero 'mediapipe' no está instalado. "
                    "Añádelo a requirements.txt e implementa read_frame()/get_gesture()."
                )
                self.enabled = False

    def read_frame(self, frame):
        """Punto de extensión: procesar un frame de cámara y devolver landmarks."""
        raise NotImplementedError(
            "Tracking de gestos no implementado en el proyecto original. "
            "Implementa aquí la lógica de MediaPipe Hands si la necesitas."
        )

    def get_gesture(self):
        """Punto de extensión: mapear landmarks a un gesto (rotar, zoom, seleccionar)."""
        return None
