from __future__ import annotations

import numpy as np


def crop_image(
    img: np.ndarray,
    target_width: int,
    target_height: int,
    center_point: tuple[int, int],
    proportion: float,
) -> np.ndarray:
    """Crop an image around a center point with adjustable horizontal position."""
    if target_width <= 0 or target_height <= 0:
        raise ValueError("target_width and target_height must be positive")
    if not 0 < proportion < 1:
        raise ValueError("proportion must be between 0 and 1")

    height, width = img.shape[:2]
    crop_width = min(target_width, width)
    crop_height = min(target_height, height)
    center_x, center_y = center_point

    ideal_x_in_crop = int(crop_width * proportion)
    crop_x = center_x - ideal_x_in_crop
    crop_y = int(center_y - crop_height // 2)

    crop_x = max(0, min(crop_x, width - crop_width))
    crop_y = max(0, min(crop_y, height - crop_height))

    return img[crop_y : crop_y + crop_height, crop_x : crop_x + crop_width]
