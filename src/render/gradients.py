"""
render/gradients.py
Generación matemática de fondos degradados (radial, lineal, starburst,
nebulosa). Extraído 1:1 de la clase `GradientBackground` del monolito
original.
"""

import math

import numpy as np


class GradientBackground:
    """Genera fondos degradados matemáticamente."""

    @staticmethod
    def radial_gradient(width, height, center_x=0.5, center_y=0.5,
                         inner_color=(0.02, 0.02, 0.06),
                         outer_color=(0.0, 0.0, 0.0),
                         inner_radius=0.3):
        image = np.zeros((height, width, 3), dtype=np.float32)
        for y in range(height):
            for x in range(width):
                nx = x / width
                ny = y / height
                dx = nx - center_x
                dy = ny - center_y
                dist = math.sqrt(dx * dx + dy * dy)
                t = min(dist / inner_radius, 1.0)
                r = inner_color[0] * (1 - t) + outer_color[0] * t
                g = inner_color[1] * (1 - t) + outer_color[1] * t
                b = inner_color[2] * (1 - t) + outer_color[2] * t
                image[y, x] = [r, g, b]
        return image

    @staticmethod
    def linear_gradient(width, height, direction='vertical',
                         color1=(0.02, 0.02, 0.06),
                         color2=(0.0, 0.0, 0.0)):
        image = np.zeros((height, width, 3), dtype=np.float32)
        for y in range(height):
            for x in range(width):
                if direction == 'vertical':
                    t = y / height
                elif direction == 'horizontal':
                    t = x / width
                elif direction == 'diagonal':
                    t = (x + y) / (width + height)
                else:
                    t = y / height
                r = color1[0] * (1 - t) + color2[0] * t
                g = color1[1] * (1 - t) + color2[1] * t
                b = color1[2] * (1 - t) + color2[2] * t
                image[y, x] = [r, g, b]
        return image

    @staticmethod
    def starburst_gradient(width, height, center_x=0.5, center_y=0.5,
                            color1=(0.02, 0.02, 0.06),
                            color2=(0.0, 0.0, 0.0),
                            color3=(0.0, 0.05, 0.0),
                            num_rays=8):
        image = np.zeros((height, width, 3), dtype=np.float32)
        for y in range(height):
            for x in range(width):
                nx = x / width - center_x
                ny = y / height - center_y
                dist = math.sqrt(nx * nx + ny * ny)
                angle = math.atan2(ny, nx)
                ray_factor = (math.cos(angle * num_rays / 2) ** 2)
                t1 = min(dist * 2, 1.0)
                t2 = ray_factor * 0.5 + 0.5
                r = color1[0] * (1 - t1) + color2[0] * t1 + color3[0] * t2 * 0.1
                g = color1[1] * (1 - t1) + color2[1] * t1 + color3[1] * t2 * 0.1
                b = color1[2] * (1 - t1) + color2[2] * t1 + color3[2] * t2 * 0.1
                image[y, x] = [np.clip(r, 0, 1), np.clip(g, 0, 1), np.clip(b, 0, 1)]
        return image

    @staticmethod
    def nebula_gradient(width, height, center_x=0.5, center_y=0.5,
                         colors=[(0.02, 0.02, 0.06), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)]):
        image = np.zeros((height, width, 3), dtype=np.float32)
        centers = [
            (0.3, 0.3, (0.1, 0.0, 0.1)),
            (0.7, 0.7, (0.0, 0.05, 0.1)),
            (0.3, 0.7, (0.05, 0.0, 0.05)),
            (0.7, 0.3, (0.0, 0.02, 0.08)),
        ]
        for y in range(height):
            for x in range(width):
                nx = x / width
                ny = y / height
                r, g, b = 0.02, 0.02, 0.06
                for cx, cy, color in centers:
                    dx = nx - cx
                    dy = ny - cy
                    dist = math.sqrt(dx * dx + dy * dy)
                    factor = math.exp(-dist * 4) * 0.3
                    r += color[0] * factor
                    g += color[1] * factor
                    b += color[2] * factor
                image[y, x] = [np.clip(r, 0, 1), np.clip(g, 0, 1), np.clip(b, 0, 1)]
        return image
