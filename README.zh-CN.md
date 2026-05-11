# 图像批量增强、旋转与裁剪工具

这是一个用于批量图像预处理的 Python 工具，可以对图像进行增强、亮斑检测、围绕检测中心旋转，并裁剪得到后续分析所需的图像区域。

项目同时提供 Tkinter 图形界面和命令行入口。

## 功能

- 批量处理 `.png`、`.jpg`、`.jpeg`、`.tif`、`.tiff`、`.bmp` 图像
- 支持包含中文字符的路径
- 可选亮度/对比度增强
- 基于亮斑连通域的自适应旋转
- 支持固定角度旋转
- 围绕检测到的旋转中心裁剪
- 支持亮度、对比度、检测阈值、裁剪比例、参考线等高级参数
- 提供 GUI 和 CLI 两种入口

## 项目结构

```text
.
├── src/
│   └── image_batch_enhance_rotate_crop/
│       ├── cropping.py       # 裁剪逻辑
│       ├── enhancement.py    # 图像增强
│       ├── rotation.py       # 旋转与亮斑检测
│       ├── processor.py      # 批处理流程
│       ├── cli.py            # 命令行入口
│       └── ui.py             # 图形界面
├── tests/
├── pyproject.toml
├── run_gui.py
└── README.md
```

## 安装

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
```

## 启动图形界面

在项目根目录运行：

```bash
python run_gui.py
```

安装为开发模式后，也可以运行：

```bash
image-batch-process-gui
```

## 命令行使用

```bash
image-batch-process "输入文件夹" "输出文件夹" --center-number 1 --crop-proportion 0.5
```

常用参数：

- `--no-enhance`: 跳过图像增强
- `--no-rotate`: 跳过旋转
- `--no-crop`: 跳过裁剪
- `--fixed-angle 15`: 使用固定角度旋转，单位为度
- `--center-number 2`: 使用第二大亮斑作为旋转中心
- `--brightness 1.2`: 亮度增强倍数
- `--contrast 1.5`: 对比度增强倍数
- `--spot-threshold 16`: 亮斑检测阈值
- `--line-threshold 16`: 线状区域/主轴检测阈值
- `--crop-proportion 0.67`: 将中心点放在裁剪宽度的 67% 位置
- `--crop-scale 0.5`: 裁剪宽高占原图宽高的比例
- `--no-reference`: 不绘制旋转参考线和中心标记

## 注意事项

- 处理大量图像前，建议先用少量样本测试参数。
- 如果启用裁剪但未检测到旋转中心，该图像会被标记为失败。
- 输出结果建议保存到仓库外部，或保存到已被 `.gitignore` 忽略的目录中。
