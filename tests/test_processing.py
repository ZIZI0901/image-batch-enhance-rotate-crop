import numpy as np
import pytest

from image_batch_enhance_rotate_crop.cropping import crop_image
from image_batch_enhance_rotate_crop.enhancement import enhance_image
from image_batch_enhance_rotate_crop.rotation import rotate_image
from image_batch_enhance_rotate_crop.cli import main as cli_main
from image_batch_enhance_rotate_crop.processor import (
    ProcessingOptions,
    process_folder,
    read_image,
)


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


def test_processing_options_reject_crop_without_rotation():
    options = ProcessingOptions(enhance=True, rotate=False, crop=True)

    with pytest.raises(ValueError, match="Cropping requires rotation"):
        options.validate()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("brightness_factor", 0),
        ("contrast_factor", -1),
        ("center_number", 0),
        ("spot_threshold", 256),
        ("line_threshold", -1),
        ("crop_proportion", 1),
        ("crop_scale", 0),
    ],
)
def test_processing_options_validate_numeric_ranges(field, value):
    values = {field: value}
    options = ProcessingOptions(**values)

    with pytest.raises(ValueError):
        options.validate()


def test_process_folder_supports_unicode_paths(tmp_path):
    input_dir = tmp_path / "输入图像"
    output_dir = tmp_path / "处理结果"
    input_dir.mkdir()

    image = np.zeros((80, 120), dtype=np.uint8)
    image[35:46, 82:93] = 255
    image[39:42, 15:86] = 120
    import cv2

    ok, encoded = cv2.imencode(".png", image)
    assert ok
    encoded.tofile(str(input_dir / "样例.png"))

    options = ProcessingOptions(
        enhance=False,
        fixed_angle=0,
        spot_threshold=200,
        line_threshold=50,
        crop_scale=0.5,
        draw_rotation_reference=False,
    )
    results = process_folder(input_dir, output_dir, options)

    assert len(results) == 1
    assert results[0].success
    output = read_image(output_dir / "样例.png")
    assert output.shape == (40, 60)


def test_cli_returns_two_for_invalid_configuration(monkeypatch, tmp_path, capsys):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    monkeypatch.setattr(
        "sys.argv",
        [
            "image-batch-process",
            str(input_dir),
            str(tmp_path / "output"),
            "--no-rotate",
        ],
    )

    assert cli_main() == 2
    assert "Cropping requires rotation" in capsys.readouterr().err


def test_cli_returns_zero_when_all_files_succeed(monkeypatch, tmp_path, capsys):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    image = np.full((12, 16), 80, dtype=np.uint8)
    import cv2

    ok, encoded = cv2.imencode(".png", image)
    assert ok
    encoded.tofile(str(input_dir / "image.png"))
    monkeypatch.setattr(
        "sys.argv",
        [
            "image-batch-process",
            str(input_dir),
            str(tmp_path / "output"),
            "--no-rotate",
            "--no-crop",
        ],
    )

    assert cli_main() == 0
    assert "Processed 1 file(s), 0 failed" in capsys.readouterr().out
