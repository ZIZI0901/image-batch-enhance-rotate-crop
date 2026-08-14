# 图像批量增强、对齐与裁剪工具

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-5C3EE8?logo=opencv&logoColor=white)](https://opencv.org/)
[![Tests](https://github.com/ZIZI0901/image-batch-enhance-rotate-crop/actions/workflows/python.yml/badge.svg)](https://github.com/ZIZI0901/image-batch-enhance-rotate-crop/actions/workflows/python.yml)

[English](README.md)

这是一个用于批量图像增强、方向校正和裁剪的Python工具。它可以定位高亮参考区域、估计主体方向，并围绕检测中心完成旋转和裁剪。

项目同时提供 Tkinter 图形界面、命令行入口和可复用的 Python API。

## 效果演示

示例图片由`examples/generate_demo.py`生成。

| 合成输入图像 | 对齐与裁剪结果 |
|---|---|
| ![合成输入](examples/assets/synthetic_input.png) | ![处理结果](examples/assets/synthetic_output.png) |

可以在本地重新生成：

```bash
python examples/generate_demo.py
```

## 处理流程

```text
输入图像
  → 灰度转换
  → 亮度与对比度增强
  → 基于阈值的高亮区域检测
  → 加权PCA主体方向估计
  → 围绕检测中心旋转
  → 按中心位置和尺寸裁剪
  → 输出图像及逐文件处理结果
```

## 主要功能

- 批量处理 `.png`、`.jpg`、`.jpeg`、`.tif`、`.tiff` 和 `.bmp`
- 支持中文文件名及中文目录
- 可选亮度与对比度增强
- 按面积排名选择高亮连通域
- 使用加权主方向估计进行自适应对齐
- 支持固定角度旋转，便于受控实验
- 支持调整裁剪大小及检测中心在裁剪区域中的水平位置
- 单张图像失败不会中断整批任务，并提供逐文件结果
- 提供桌面GUI、CLI和Python API
- 通过GitHub Actions在Windows环境执行自动化测试

## 安装

要求Python 3.9或更高版本。

```bash
git clone https://github.com/ZIZI0901/image-batch-enhance-rotate-crop.git
cd image-batch-enhance-rotate-crop
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

macOS/Linux：

```bash
source .venv/bin/activate
python -m pip install -e .
```

## 快速使用

### 图形界面

```bash
python run_gui.py
```

安装项目后也可以运行：

```bash
image-batch-process-gui
```

### 命令行

```bash
image-batch-process "输入目录" "输出目录" \
  --spot-threshold 180 \
  --line-threshold 55 \
  --crop-scale 0.55 \
  --crop-proportion 0.65
```

全部文件成功时CLI返回退出码`0`，存在单文件失败时返回`1`，输入或配置无效时返回`2`，便于脚本和自动化任务判断结果。

常用参数：

| 参数 | 含义 | 默认值 |
|---|---|---:|
| `--no-enhance` | 关闭亮度/对比度增强 | 关闭 |
| `--no-rotate` | 关闭图像对齐 | 关闭 |
| `--no-crop` | 关闭裁剪 | 关闭 |
| `--brightness` | 亮度倍数 | `1.2` |
| `--contrast` | 对比度倍数 | `1.5` |
| `--center-number` | 作为中心的高亮连通域面积排名 | `1` |
| `--fixed-angle` | 使用固定旋转角度 | 自适应 |
| `--spot-threshold` | 高亮区域检测初始阈值 | `16` |
| `--line-threshold` | 主方向估计阈值 | `16` |
| `--crop-proportion` | 中心点在裁剪区域中的水平位置 | `0.5` |
| `--crop-scale` | 裁剪宽高相对原图的比例 | `0.5` |
| `--no-reference` | 不绘制中心点和参考线 | 关闭 |

裁剪依赖旋转阶段检测到的中心，因此使用`--no-rotate`时必须同时使用`--no-crop`。

## Python API

```python
from image_batch_enhance_rotate_crop.processor import ProcessingOptions, process_folder

options = ProcessingOptions(
    brightness_factor=1.15,
    contrast_factor=1.35,
    spot_threshold=180,
    line_threshold=55,
    crop_scale=0.55,
    crop_proportion=0.65,
    draw_rotation_reference=False,
)

results = process_folder("input", "output", options)
for result in results:
    print(result.filename, result.success, result.message)
```

## 算法说明

1. 对高亮连通域轮廓取均值得到旋转中心。
2. 在阈值前景中选取检测中心指定一侧的像素。
3. 计算带距离权重的协方差矩阵，以最大特征值对应的特征向量表示主体方向。
4. 围绕检测中心旋转图像，并保持原始画布大小。
5. 按设定比例裁剪，使检测中心位于裁剪区域中的指定水平位置，适合目标区域不对称的情况。

这套方法主要用于参考亮斑明显、主体方向较清晰的图像，不适合复杂背景下的通用图像配准。

## 使用限制

- 检测过程假设参考区域明显亮于周围背景。
- 大批量处理前，应使用代表性样本标定阈值。
- 强杂波或多个面积相近的高亮区域可能导致中心选择错误。
- 旋转保持原始画布大小，靠近边缘的内容可能被裁掉。
- 当前裁剪为轴对齐裁剪，且依赖中心检测成功。

## 开发与测试

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

重新生成合成示例：

```bash
python examples/generate_demo.py
```

## 项目结构

```text
.
├── .github/workflows/python.yml
├── examples/
│   ├── assets/
│   └── generate_demo.py
├── src/image_batch_enhance_rotate_crop/
│   ├── cli.py
│   ├── cropping.py
│   ├── enhancement.py
│   ├── processor.py
│   ├── rotation.py
│   └── ui.py
├── tests/test_processing.py
├── pyproject.toml
└── run_gui.py
```
