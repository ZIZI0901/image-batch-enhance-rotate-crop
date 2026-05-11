# Batch Image Enhancement, Rotation, and Cropping Tool

中文文档: [README.zh-CN.md](README.zh-CN.md)

This project provides a Python tool for batch image preprocessing. It can enhance images, detect a bright region, rotate images around the detected center, and crop the result for downstream analysis.

The project includes both a Tkinter graphical interface and a command-line interface.

## Features

- Batch process `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`, and `.bmp` files
- Supports paths containing Chinese characters
- Optional brightness/contrast enhancement
- Adaptive rotation based on bright connected components
- Optional fixed-angle rotation
- Crop around the detected rotation center
- Advanced parameters for brightness, contrast, detection thresholds, crop scale, and reference markers
- GUI and CLI entry points

## Project Structure

```text
.
├── src/
│   └── image_batch_enhance_rotate_crop/
│       ├── cropping.py
│       ├── enhancement.py
│       ├── rotation.py
│       ├── processor.py
│       ├── cli.py
│       └── ui.py
├── tests/
├── pyproject.toml
├── run_gui.py
└── README.md
```

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
```

On macOS/Linux:

```bash
source .venv/bin/activate
python -m pip install -e .
```

## Run the GUI

From the project root:

```bash
python run_gui.py
```

After installation, you can also run:

```bash
image-batch-process-gui
```

## Run from Command Line

```bash
image-batch-process "path/to/input" "path/to/output" --center-number 1 --crop-proportion 0.5
```

Common options:

- `--no-enhance`: skip image enhancement
- `--no-rotate`: skip rotation
- `--no-crop`: skip cropping
- `--fixed-angle 15`: rotate by a fixed angle in degrees
- `--center-number 2`: use the second largest bright spot as the rotation center
- `--brightness 1.2`: brightness multiplier
- `--contrast 1.5`: contrast multiplier
- `--spot-threshold 16`: threshold used to detect bright spots
- `--line-threshold 16`: threshold used to detect the line/axis region
- `--crop-proportion 0.67`: position the center point at 67% of the crop width
- `--crop-scale 0.5`: crop width/height as a ratio of the original image size
- `--no-reference`: do not draw rotation reference markers

## Notes

- Test parameters on a small image set before processing a large folder.
- If cropping is enabled and no rotation center is detected, that image is reported as failed.
- Generated outputs should be stored outside the repository or in an ignored folder.
