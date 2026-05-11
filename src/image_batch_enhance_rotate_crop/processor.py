from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

from image_batch_enhance_rotate_crop.cropping import crop_image
from image_batch_enhance_rotate_crop.enhancement import enhance_image, to_grayscale
from image_batch_enhance_rotate_crop.rotation import rotate_image


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


@dataclass(frozen=True)
class ProcessingOptions:
    enhance: bool = True
    rotate: bool = True
    crop: bool = True
    brightness_factor: float = 1.2
    contrast_factor: float = 1.5
    center_number: int = 1
    fixed_angle: float | None = None
    spot_threshold: int = 16
    line_threshold: int = 16
    crop_proportion: float = 0.5
    crop_scale: float = 0.5
    draw_rotation_reference: bool = True


@dataclass(frozen=True)
class ProcessingResult:
    filename: str
    success: bool
    message: str = ""


ProgressCallback = Callable[[ProcessingResult, int, int], None]


def process_folder(
    input_dir: str | Path,
    output_dir: str | Path,
    options: ProcessingOptions,
    progress_callback: ProgressCallback | None = None,
) -> list[ProcessingResult]:
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"Input folder does not exist: {input_path}")
    if not input_path.is_dir():
        raise NotADirectoryError(f"Input path is not a folder: {input_path}")

    output_path.mkdir(parents=True, exist_ok=True)
    image_files = sorted(path for path in input_path.iterdir() if path.suffix.lower() in IMAGE_EXTENSIONS)
    if not image_files:
        raise FileNotFoundError("No supported image files found in the input folder")

    results: list[ProcessingResult] = []
    total = len(image_files)
    for index, image_path in enumerate(image_files, start=1):
        try:
            result_image = process_image_file(image_path, options)
            save_image(output_path / image_path.name, result_image)
            result = ProcessingResult(image_path.name, True)
        except Exception as exc:
            result = ProcessingResult(image_path.name, False, str(exc))

        results.append(result)
        if progress_callback:
            progress_callback(result, index, total)

    return results


def process_image_file(image_path: str | Path, options: ProcessingOptions) -> np.ndarray:
    img = read_image(image_path)
    original_height, original_width = img.shape[:2]
    processed = to_grayscale(img)
    rotation_center: tuple[int, int] | None = None

    if options.enhance:
        processed = enhance_image(
            processed,
            brightness_factor=options.brightness_factor,
            contrast_factor=options.contrast_factor,
        )

    if options.rotate:
        processed, rotation_center = rotate_image(
            processed,
            center_number=options.center_number,
            fixed_angle=options.fixed_angle,
            spot_thresh=options.spot_threshold,
            line_thresh=options.line_threshold,
            draw_contour=options.draw_rotation_reference,
        )

    if options.crop:
        if rotation_center is None:
            raise ValueError("Rotation center was not detected; crop cannot be applied")
        processed = crop_image(
            processed,
            target_width=max(1, int(original_width * options.crop_scale)),
            target_height=max(1, int(original_height * options.crop_scale)),
            center_point=rotation_center,
            proportion=options.crop_proportion,
        )

    return processed


def read_image(path: str | Path) -> np.ndarray:
    image_path = Path(path)
    img = cv2.imdecode(np.fromfile(str(image_path), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Unable to read image: {image_path.name}")
    return img


def save_image(path: str | Path, img: np.ndarray) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    extension = output_path.suffix or ".png"
    ok, encoded = cv2.imencode(extension, img)
    if not ok:
        raise ValueError(f"Unable to encode output image: {output_path.name}")
    encoded.tofile(str(output_path))
