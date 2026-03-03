# Batch Image Enhancement, Rotation, and Cropping Tool

In fields such as biological imaging, materials science, and industrial inspection, standardized image preprocessing is often required to extract meaningful information from regions of interest.

This tool is designed for batch image processing workflows that require rotation and cropping centered on the brightest region of an image (i.e., the pixel with the maximum grayscale value). It integrates image enhancement, automatic rotation based on the brightest spot, and subsequent cropping into a unified pipeline.

The program provides an interactive graphical user interface (GUI) for convenient operation while also allowing advanced users to flexibly adjust processing parameters and algorithms by modifying configuration files. It offers an efficient and extensible image preprocessing solution for researchers and engineers.

---

## Usage

* This program is intended for batch processing of images that require rotation and cropping centered on the brightest region (maximum grayscale value).

* Run the main program file `main_ui.py` to launch the graphical user interface.

---

## Functional Modules

### 1. Image Enhancement (`image_enhancement.py`)

Before rotation and cropping, images can be enhanced to emphasize the target bright spot and suppress noise.

Several basic enhancement algorithms are provided by default, including contrast stretching and histogram equalization. Users may modify or replace the enhancement methods by editing `image_enhancement.py`, allowing adaptation to different imaging conditions and experimental requirements.

---

### 2. Image Rotation (`image_rotation.py`)

By default, the rotation center is defined as the pixel with the highest grayscale value (the brightest region).

Additionally, users can adjust the **“Head Node Index”** parameter via the GUI to select a bright spot of a specific brightness rank as the rotation center (e.g., the second brightest spot).

Two rotation modes are available:

* **Adaptive Rotation**
  If the target bright region exhibits a linear distribution (e.g., filament-like structures or fluorescently labeled nerve fibers), the program automatically fits its principal axis and rotates the image to align it horizontally.

* **Fixed-Angle Rotation**
  Users may manually input a rotation angle (in degrees). The image will be rotated around the selected center point by the specified angle.

Advanced users can extend or replace the rotation algorithms by modifying `image_rotation.py`, for example:

* Implementing PCA-based orientation alignment
* Manually specifying a rotation axis
* Integrating custom geometric transformation methods

---

### 3. Image Cropping (`image_cropping.py`)

After rotation, the image is cropped.

The cropping region size (width and height) is defined by variables within `image_cropping.py`. By default, the cropping center coincides with the rotation center (the brightest point).

This module supports customized cropping strategies, such as:

* Automatically determining the crop size based on bright spot dimensions
* Preserving a fixed margin around the target region
* Implementing rule-based or adaptive cropping logic

Users can adjust these behaviors by editing the corresponding configuration file.

---

## Development Status and Notes

### Current Version

This tool is still under active development. The core processing workflow is functional, but some advanced configurations currently require direct modification of Python source files.

### Important Notes

* Ensure that each input image contains at least one detectable bright spot. Otherwise, the rotation center may not be correctly identified.

* When modifying configuration files, carefully follow the in-code comments to avoid syntax errors.

* It is strongly recommended to test parameters on a small sample set before processing large batches of images.

---

## Future Improvements

Future versions will focus on:

* Enhancing the GUI with more intuitive parameter controls
* Reducing the need for manual code modification
* Integrating additional general-purpose image enhancement and rotation algorithms
* Improving overall usability and robustness

User feedback and suggestions are welcome to help improve and refine the tool.
