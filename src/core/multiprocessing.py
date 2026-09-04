"""
core/multiprocessing.py

AVISO: el monolito original NO usaba multiprocessing real. Las 8 barras
de "Cerebro N" se actualizaban con incrementos aleatorios en un QTimer,
puramente decorativo. Esta clase reproduce EXACTAMENTE ese comportamiento
(mismo cálculo, mismos rangos) para no cambiar el look final, pero lo
aísla en su propio módulo para que si algún día quieres reemplazarlo por
un multiprocessing.Pool real, solo tengas que tocar este archivo.
"""

import numpy as np

from src.utils.config import NUM_SIMULATED_BRAINS


class ProcessSimulator:
    """Simula la carga de N "cerebros" de procesamiento en paralelo."""

    def __init__(self, num_brains=NUM_SIMULATED_BRAINS):
        self.num_brains = num_brains
        self.values = [0] * num_brains

    def tick(self):
        """Avanza un paso de simulación y devuelve los nuevos valores (0-100)."""
        for i in range(self.num_brains):
            increment = np.random.randint(1, 5) * (1 + (i % 3) * 0.2)
            new_val = self.values[i] + increment
            if new_val > 100:
                new_val = 0
            self.values[i] = int(new_val)
        return self.values
