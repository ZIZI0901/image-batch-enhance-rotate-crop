from __future__ import annotations

import argparse
from pathlib import Path
import sys

from image_batch_enhance_rotate_crop.processor import ProcessingOptions, process_folder


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Batch enhance, rotate, and crop image files.",
    )
    parser.add_argument("input_dir", type=Path, help="Folder containing images.")
    parser.add_argument("output_dir", type=Path, help="Folder for processed images.")
    parser.add_argument("--no-enhance", action="store_true", help="Disable enhancement.")
    parser.add_argument("--no-rotate", action="store_true", help="Disable rotation.")
    parser.add_argument("--no-crop", action="store_true", help="Disable cropping.")
    parser.add_argument("--brightness", type=float, default=1.2, help="Brightness multiplier used during enhancement.")
    parser.add_argument("--contrast", type=float, default=1.5, help="Contrast multiplier used during enhancement.")
    parser.add_argument("--center-number", type=int, default=1, help="Bright spot rank used as rotation center.")
    parser.add_argument("--fixed-angle", type=float, help="Fixed rotation angle in degrees.")
    parser.add_argument("--spot-threshold", type=int, default=16, help="Threshold used to detect bright spots.")
    parser.add_argument("--line-threshold", type=int, default=16, help="Threshold used to detect the line/axis region.")
    parser.add_argument("--crop-proportion", type=float, default=0.5, help="Horizontal position of center point inside crop.")
    parser.add_argument("--crop-scale", type=float, default=0.5, help="Crop width/height as a ratio of original image size.")
    parser.add_argument("--no-reference", action="store_true", help="Do not draw rotation reference markers.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    options = ProcessingOptions(
        enhance=not args.no_enhance,
        rotate=not args.no_rotate,
        crop=not args.no_crop,
        brightness_factor=args.brightness,
        contrast_factor=args.contrast,
        center_number=args.center_number,
        fixed_angle=args.fixed_angle,
        spot_threshold=args.spot_threshold,
        line_threshold=args.line_threshold,
        crop_proportion=args.crop_proportion,
        crop_scale=args.crop_scale,
        draw_rotation_reference=not args.no_reference,
    )
    try:
        results = process_folder(args.input_dir, args.output_dir, options)
    except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    failures = [result for result in results if not result.success]
    print(f"Processed {len(results)} file(s), {len(failures)} failed.")
    for failure in failures:
        print(f"{failure.filename}: {failure.message}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
