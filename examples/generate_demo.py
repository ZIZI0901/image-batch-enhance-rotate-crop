"""Generate a synthetic, privacy-safe example for the project README."""

from pathlib import Path

import cv2
import numpy as np

from image_batch_enhance_rotate_crop.processor import ProcessingOptions, process_image_file, save_image


def create_input() -> np.ndarray:
    height, width = 480, 720
    canvas = np.zeros((height, width), dtype=np.uint8)
    gradient = np.linspace(5, 35, width, dtype=np.uint8)
    canvas[:] = gradient

    center = (520, 180)
    cv2.line(canvas, (120, 360), center, 95, 18, cv2.LINE_AA)
    cv2.circle(canvas, center, 34, 230, -1, cv2.LINE_AA)
    cv2.circle(canvas, center, 12, 255, -1, cv2.LINE_AA)
    noise = np.random.default_rng(7).normal(0, 3, canvas.shape)
    return np.clip(canvas.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "assets"
    output_dir.mkdir(parents=True, exist_ok=True)
    input_path = output_dir / "synthetic_input.png"
    save_image(input_path, create_input())

    options = ProcessingOptions(
        brightness_factor=1.15,
        contrast_factor=1.35,
        spot_threshold=180,
        line_threshold=55,
        crop_scale=0.55,
        crop_proportion=0.65,
        draw_rotation_reference=True,
    )
    result = process_image_file(input_path, options)
    save_image(output_dir / "synthetic_output.png", result)
    print(f"Generated demo assets in {output_dir}")


if __name__ == "__main__":
    main()
