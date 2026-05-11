import numpy as np

from image_batch_enhance_rotate_crop.cropping import crop_image
from image_batch_enhance_rotate_crop.enhancement import enhance_image
from image_batch_enhance_rotate_crop.rotation import rotate_image


def test_crop_image_respects_target_size():
    img = np.arange(100, dtype=np.uint8).reshape(10, 10)

    cropped = crop_image(img, 4, 6, center_point=(5, 5), proportion=0.5)

    assert cropped.shape == (6, 4)


def test_enhance_image_preserves_shape_and_dtype():
    img = np.full((4, 4), 100, dtype=np.uint8)

    enhanced = enhance_image(img)

    assert enhanced.shape == img.shape
    assert enhanced.dtype == img.dtype


def test_rotate_image_returns_center_for_fixed_angle():
    img = np.zeros((20, 20), dtype=np.uint8)
    img[10, 10] = 255

    rotated, center = rotate_image(img, fixed_angle=0, draw_contour=False)

    assert rotated.shape == img.shape
    assert center == (10, 10)
