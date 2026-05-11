from __future__ import annotations

import cv2
import numpy as np


def enhance_image(
    img: np.ndarray,
    brightness_factor: float = 1.2,
    contrast_factor: float = 1.5,
) -> np.ndarray:
    """Adjust brightness and contrast while preserving the input dtype shape."""
    img_float = img.astype(np.float32)
    max_value = 65535.0 if img.dtype == np.uint16 else 255.0
    img_float = img_float / max_value

    brightened = np.clip(img_float * brightness_factor, 0, 1)
    contrasted = np.clip((brightened - 0.5) * contrast_factor + 0.5, 0, 1)
    return (contrasted * max_value).astype(img.dtype)


def to_grayscale(img: np.ndarray) -> np.ndarray:
    if img.ndim == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
