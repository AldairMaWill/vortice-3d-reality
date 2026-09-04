import numpy as np

from src.vision.filters import ImageProcessor


def _dummy_image():
    return np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)


def test_apply_grayscale_returns_3_channels():
    proc = ImageProcessor("test", "test")
    result = proc.apply_grayscale(_dummy_image())
    assert result is not None
    assert result.shape[2] == 3


def test_apply_negative_inverts_pixels():
    proc = ImageProcessor("test", "test")
    img = np.zeros((4, 4, 3), dtype=np.uint8)
    result = proc.apply_negative(img)
    assert (result == 255).all()


def test_apply_thermal_vision_returns_image():
    proc = ImageProcessor("test", "test")
    result = proc.apply_thermal_vision(_dummy_image())
    assert result is not None
    assert result.shape[:2] == (64, 64)


def test_process_defaults_to_grayscale_for_unknown_mode():
    proc = ImageProcessor("test", "test")
    result = proc.process(_dummy_image(), mode="modo_inexistente")
    assert result is not None


def test_filters_handle_none_gracefully():
    proc = ImageProcessor("test", "test")
    assert proc.apply_grayscale(None) is None
    assert proc.apply_negative(None) is None
    assert proc.apply_thermal_vision(None) is None
