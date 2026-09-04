"""
utils/logger.py
Logging estructurado y centralizado para todo el proyecto. El monolito
original no tenía logging (solo un par de `print` para debug del árbol);
aquí se formaliza sin cambiar el comportamiento visible de la app.
"""

import logging
import sys

from src.utils.config import LOG_LEVEL

_CONFIGURED = False


def get_logger(name: str) -> logging.Logger:
    """Devuelve un logger configurado de forma consistente en todo el proyecto."""
    global _CONFIGURED

    if not _CONFIGURED:
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
            format="[%(asctime)s] %(levelname)-8s %(name)s: %(message)s",
            datefmt="%H:%M:%S",
            stream=sys.stdout,
        )
        _CONFIGURED = True

    return logging.getLogger(name)
