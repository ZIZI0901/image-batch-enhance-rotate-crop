import cv2
import numpy as np


def rotate_image(img, center_number=1, fixed_angle=None, spot_thresh=16, line_thresh=16, draw_contour=True):
    """
    旋转图像，使光纤锥方向水平，头结点位于最右侧。

    参数:
        img: 输入灰度图像
        center_number: 选择第几个光斑作为头结点 (1表示最大光斑, 2表示第二大, 以此类推)
        fixed_angle: 如果提供，则使用固定角度旋转（以头结点为中心），否则自动计算角度
        spot_thresh: 提取光斑的初始阈值
        line_thresh: 提取光纤锥上光点的阈值
        draw_contour: 是否绘制标记和直线

    返回:
        rotated: 旋转后的图像（如果draw_contour=True则为彩色图，否则为灰度图）
        rotated_head_point: 旋转后头结点的坐标 (x, y)，若未找到头结点则返回None
    """
    # ---------- 1. 自适应找光斑 ----------
    head_spot = None
    temp_thresh = spot_thresh

    # 如果需要找指定序号的光斑（center_number > 1），则需要收集所有光斑并排序
    if center_number > 1:
        spots = []
        # 尝试降低阈值直到找到足够的光斑
        for i in range(10):  # 最多尝试10次降低阈值
            _, spot_mask = cv2.threshold(img, temp_thresh, 255, cv2.THRESH_BINARY)
            spot_contours, _ = cv2.findContours(spot_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if spot_contours:
                spots = list(spot_contours)
                if len(spots) >= center_number:
                    break
            temp_thresh -= 16
            if temp_thresh < line_thresh:
                temp_thresh = line_thresh
                break

        if spots:
            # 按面积排序（从大到小）
            spots_sorted = sorted(spots, key=cv2.contourArea, reverse=True)
            index = min(center_number - 1, len(spots_sorted) - 1)
            if index < 0:
                index = 0
            head_spot = spots_sorted[index]
    else:
        # 默认行为：快速找到最大光斑
        temp_thresh = spot_thresh
        while temp_thresh >= line_thresh:
            _, spot_mask = cv2.threshold(img, temp_thresh, 255, cv2.THRESH_BINARY)
            spot_contours, _ = cv2.findContours(spot_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if spot_contours:
                head_spot = max(spot_contours, key=cv2.contourArea)
                break
            temp_thresh -= 16

    if head_spot is None:
        # 没找到光斑，返回原图和None
        return img, None

    # 计算头结点为光斑的质心
    head_point = tuple(np.mean(head_spot.reshape(-1, 2), axis=0).astype(int))

    # ---------- 2. 判断是否使用固定角度旋转 ----------
    if fixed_angle is not None:
        # 使用固定角度旋转
        height, width = img.shape[:2]
        center = (float(head_point[0]), float(head_point[1]))  # 旋转中心为光斑质心
        angle_deg = fixed_angle

        # 旋转图片
        rot_mat = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
        rotated = cv2.warpAffine(img, rot_mat, (width, height),
                                 flags=cv2.INTER_CUBIC,
                                 borderMode=cv2.BORDER_CONSTANT, borderValue=0)

        # 头结点坐标变换
        head_h = np.array([head_point[0], head_point[1], 1])
        rotated_head = np.dot(rot_mat, head_h).astype(int)
        rotated_head_point = (rotated_head[0], rotated_head[1])

        # 可视化
        if draw_contour:
            rotated_color = cv2.cvtColor(rotated, cv2.COLOR_GRAY2BGR)
            cv2.line(rotated_color,
                     (0, rotated_head_point[1]),
                     (width, rotated_head_point[1]),
                     (0, 255, 0), 2)
            cv2.circle(rotated_color, rotated_head_point, 8, (0, 0, 255), -1)
            cv2.circle(rotated_color, rotated_head_point, 4, (255, 255, 255), -1)
            return rotated_color, rotated_head_point

        return rotated, rotated_head_point

    # ---------- 3. 找光纤锥上所有光点 ----------
    _, line_mask = cv2.threshold(img, line_thresh, 255, cv2.THRESH_BINARY)
    line_contours, _ = cv2.findContours(line_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not line_contours:
        return img, None

    all_points = np.vstack(line_contours).squeeze().astype(np.float32)

    # 过滤右侧的光斑散点，只保留左侧光点 (x <= head_point[0])
    mask = all_points[:, 0] <= head_point[0]
    all_points = all_points[mask]
    if all_points.ndim == 1 or len(all_points) < 2:
        return img, None

    # ---------- 4. 加权直线拟合 (PCA) ----------
    # 4-1 以到头结点的距离做高斯加权
    dists = np.sqrt(((all_points - head_point) ** 2).sum(axis=1))
    sigma = 0.7 * dists.max() if dists.max() > 0 else 1.0
    weights = np.exp(-(dists ** 2) / (2 * sigma ** 2))

    # 4-2 加权重心
    Sw = weights.sum()
    if Sw == 0:
        return img, None
    mean = (all_points.T @ weights) / Sw  # [x̄, ȳ]

    # 4-3 加权协方差
    cx = all_points[:, 0] - mean[0]
    cy = all_points[:, 1] - mean[1]
    Mxx = (weights * cx * cx).sum() / Sw
    Myy = (weights * cy * cy).sum() / Sw
    Mxy = (weights * cx * cy).sum() / Sw
    cov = np.array([[Mxx, Mxy], [Mxy, Myy]])
    eigvals, eigvecs = np.linalg.eigh(cov)
    direction = eigvecs[:, np.argmax(eigvals)]  # 直线方向向量 (vx, vy)
    vx, vy = direction

    # ---------- 5. 旋转 ----------
    # 5-1 计算旋转角度
    angle_rad = np.arctan2(vy, vx)
    angle_deg = np.degrees(angle_rad)
    # 调整角度到 -90~90 度
    if angle_deg > 90:
        angle_deg -= 180
    elif angle_deg <= -90:
        angle_deg += 180

    height, width = img.shape[:2]
    center = (float(head_point[0]), float(head_point[1]))  # 旋转中心为头结点
    rot_mat = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
    rotated = cv2.warpAffine(img, rot_mat, (width, height),
                             flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_CONSTANT, borderValue=0)

    # 头结点坐标变换
    head_h = np.array([head_point[0], head_point[1], 1])
    rotated_head = np.dot(rot_mat, head_h).astype(int)
    rotated_head_point = (rotated_head[0], rotated_head[1])

    # ---------- 6. 可视化 ----------
    if draw_contour:
        rotated_color = cv2.cvtColor(rotated, cv2.COLOR_GRAY2BGR)
        # 绘制水平线
        cv2.line(rotated_color,
                 (0, rotated_head_point[1]),
                 (width, rotated_head_point[1]),
                 (0, 255, 0), 2)
        cv2.circle(rotated_color, rotated_head_point, 8, (0, 0, 255), -1)
        cv2.circle(rotated_color, rotated_head_point, 4, (255, 255, 255), -1)
        return rotated_color, rotated_head_point

    return rotated, rotated_head_point