
def crop_image(img, target_width, target_height, center_point, proportion):
    """
    以指定中心点为基础裁剪图像到目标尺寸，并根据比例调整水平位置
    参数:
        img: 输入图像
        target_width: 目标宽度
        target_height: 目标高度
        center_point: 中心点坐标 (x, y)
        proportion: 中心点x轴位置比例 (0-1)
    返回:
        裁剪后的图像
    """
    h, w = img.shape[:2]
    center_x, center_y = center_point

    # 垂直方向：确保中心点居中
    crop_y = max(0, int(center_y - target_height // 2))

    # 水平方向：根据比例调整中心点位置
    # 计算中心点在裁剪区域内的理想位置
    ideal_x_in_crop = int(target_width * proportion)

    # 根据理想位置计算裁剪起始x坐标
    crop_x = center_x - ideal_x_in_crop

    # 调整边界确保不超出图像范围
    crop_x = max(0, crop_x)
    crop_x = min(crop_x, w - target_width)

    # 确保裁剪坐标有效
    if crop_y + target_height > h:
        crop_y = h - target_height
    if crop_y < 0:
        crop_y = 0

    # 执行裁剪
    cropped = img[crop_y:crop_y + target_height, crop_x:crop_x + target_width]

    return cropped