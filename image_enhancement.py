import cv2
import numpy as np


def enhance_image(img, brightness_factor=1.2, contrast_factor=1.5):
    """
    图像增强：亮度和对比度调整
    参数:
        img: 输入图像 (BGR格式)
        brightness_factor: 亮度增强因子 (1.0表示不变)
        contrast_factor: 对比度增强因子 (1.0表示不变)
    返回:
        增强后的图像
    """
    # 转换为浮点数进行计算
    img_float = img.astype(np.float32) / 255.0

    # 亮度调整
    brightened = np.clip(img_float * brightness_factor, 0, 1)

    # 对比度调整
    contrasted = np.clip((brightened - 0.5) * contrast_factor + 0.5, 0, 1)

    # 转换回8位图像
    enhanced = (contrasted * 255).astype(np.uint8)

    return enhanced