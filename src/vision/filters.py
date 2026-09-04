"""
vision/filters.py
Filtros de procesamiento de imagen con OpenCV. Extraído 1:1 de la clase
`ImageProcessor` del monolito original — misma lógica, sin cambios de
comportamiento.
"""

from collections import deque

import cv2
import numpy as np

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ImageProcessor:
    """Procesador con filtros para mejor visualización."""

    def __init__(self, name, specialization):
        self.name = name
        self.specialization = specialization
        self.processed_image = None
        self.raw_image = None
        self.processing_queue = deque(maxlen=10)

    def apply_grayscale(self, image):
        if image is None:
            return None
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        gray = cv2.equalizeHist(gray)
        result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        return result

    def apply_negative(self, image):
        if image is None:
            return None
        return 255 - image

    def apply_warm_light(self, image):
        if image is None:
            return None
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        gray = cv2.equalizeHist(gray)
        sepia = np.zeros((gray.shape[0], gray.shape[1], 3), dtype=np.uint8)
        sepia[:, :, 0] = np.clip(gray * 0.9 + 30, 0, 255).astype(np.uint8)
        sepia[:, :, 1] = np.clip(gray * 0.8 + 40, 0, 255).astype(np.uint8)
        sepia[:, :, 2] = np.clip(gray * 0.7 + 50, 0, 255).astype(np.uint8)
        return sepia

    def apply_text_enhance(self, image):
        if image is None:
            return None
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]) / 1.0
        sharpened = cv2.filter2D(denoised, -1, kernel)
        binary = cv2.adaptiveThreshold(
            sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        result = cv2.addWeighted(denoised, 0.5, binary, 0.5, 0)
        return cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)

    def apply_original_color(self, image):
        if image is None:
            return None
        if len(image.shape) == 2:
            return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        return image.copy()

    def apply_night_vision(self, image, color_tint='green'):
        if image is None:
            return None
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        gray = cv2.equalizeHist(gray)
        edges = cv2.Laplacian(gray, cv2.CV_64F)
        edges = np.abs(edges)
        edges = np.uint8(np.clip(edges, 0, 255))
        enhanced = cv2.addWeighted(gray, 0.7, edges, 0.3, 0)

        color_map = {
            'green': (1, 0, 0), 'blue': (0, 0, 1), 'red': (0, 1, 0),
            'cyan': (0, 1, 1), 'magenta': (1, 0, 1), 'yellow': (1, 1, 0),
            'white': (1, 1, 1), 'orange': (0, 0.5, 1), 'purple': (1, 0, 0.8),
            'lime': (0.2, 1, 0)
        }
        r_factor, g_factor, b_factor = color_map.get(color_tint, (1, 0, 0))

        night_vision = np.zeros((image.shape[0], image.shape[1], 3), dtype=np.uint8)
        night_vision[:, :, 0] = (enhanced * r_factor * 0.8).astype(np.uint8)
        night_vision[:, :, 1] = (enhanced * g_factor * 0.8).astype(np.uint8)
        night_vision[:, :, 2] = (enhanced * b_factor * 0.8).astype(np.uint8)

        noise = np.random.randn(*enhanced.shape) * 3
        night_vision = night_vision.astype(np.float32)
        night_vision[:, :, 1] += noise * g_factor
        night_vision[:, :, 0] += noise * r_factor
        night_vision[:, :, 2] += noise * b_factor
        night_vision = np.clip(night_vision, 0, 255).astype(np.uint8)
        return night_vision

    def apply_thermal_vision(self, image):
        if image is None:
            return None
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        return cv2.applyColorMap(gray, cv2.COLORMAP_JET)

    def process(self, image, mode='grayscale', color_tint='green'):
        self.raw_image = image
        processors = {
            'grayscale': self.apply_grayscale,
            'negative': self.apply_negative,
            'warm_light': self.apply_warm_light,
            'text_enhance': self.apply_text_enhance,
            'original': self.apply_original_color,
            'night_vision': lambda img: self.apply_night_vision(img, color_tint),
            'thermal': self.apply_thermal_vision,
        }
        self.processed_image = processors.get(mode, self.apply_grayscale)(image)
        return self.processed_image
