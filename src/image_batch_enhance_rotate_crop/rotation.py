from __future__ import annotations

import cv2
import numpy as np


def rotate_image(
    img: np.ndarray,
    center_number: int = 1,
    fixed_angle: float | None = None,
    spot_thresh: int = 16,
    line_thresh: int = 16,
    draw_contour: bool = True,
) -> tuple[np.ndarray, tuple[int, int] | None]:
    """Rotate an image around a detected bright spot.

    The brightest connected component is used by default. ``center_number`` can
    select the second, third, etc. largest bright component.
    """
    if center_number < 1:
        raise ValueError("center_number must be greater than or equal to 1")

    gray = _ensure_gray(img)
    head_spot = _find_head_spot(gray, center_number, spot_thresh, line_thresh)
    if head_spot is None:
        return img, None

    head_point = tuple(np.mean(head_spot.reshape(-1, 2), axis=0).astype(int))
    angle_deg = fixed_angle if fixed_angle is not None else _estimate_alignment_angle(
        gray,
        head_point,
        line_thresh,
    )
    if angle_deg is None:
        return img, None

    rotated, rotated_head_point = _rotate_around_point(gray, head_point, angle_deg)

    if draw_contour:
        return _draw_reference(rotated, rotated_head_point), rotated_head_point
    return rotated, rotated_head_point


def _ensure_gray(img: np.ndarray) -> np.ndarray:
    if img.ndim == 2:
        return img
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def _find_head_spot(
    img: np.ndarray,
    center_number: int,
    spot_thresh: int,
    line_thresh: int,
) -> np.ndarray | None:
    temp_thresh = spot_thresh
    selected_contours: list[np.ndarray] = []

    while temp_thresh >= line_thresh:
        _, spot_mask = cv2.threshold(img, temp_thresh, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(spot_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            selected_contours = sorted(contours, key=cv2.contourArea, reverse=True)
            if len(selected_contours) >= center_number:
                break
        temp_thresh -= 16

    if not selected_contours:
        return None

    index = min(center_number - 1, len(selected_contours) - 1)
    return selected_contours[index]


def _estimate_alignment_angle(
    img: np.ndarray,
    head_point: tuple[int, int],
    line_thresh: int,
) -> float | None:
    _, line_mask = cv2.threshold(img, line_thresh, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(line_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    all_points = np.vstack(contours).squeeze().astype(np.float32)
    if all_points.ndim == 1:
        return None

    all_points = all_points[all_points[:, 0] <= head_point[0]]
    if len(all_points) < 2:
        return None

    dists = np.sqrt(((all_points - head_point) ** 2).sum(axis=1))
    sigma = 0.7 * dists.max() if dists.max() > 0 else 1.0
    weights = np.exp(-(dists**2) / (2 * sigma**2))

    weight_sum = weights.sum()
    if weight_sum == 0:
        return None

    mean = (all_points.T @ weights) / weight_sum
    centered = all_points - mean
    cov = np.array(
        [
            [(weights * centered[:, 0] * centered[:, 0]).sum() / weight_sum,
             (weights * centered[:, 0] * centered[:, 1]).sum() / weight_sum],
            [(weights * centered[:, 0] * centered[:, 1]).sum() / weight_sum,
             (weights * centered[:, 1] * centered[:, 1]).sum() / weight_sum],
        ]
    )
    eigvals, eigvecs = np.linalg.eigh(cov)
    vx, vy = eigvecs[:, np.argmax(eigvals)]
    angle_deg = float(np.degrees(np.arctan2(vy, vx)))

    if angle_deg > 90:
        angle_deg -= 180
    elif angle_deg <= -90:
        angle_deg += 180
    return angle_deg


def _rotate_around_point(
    img: np.ndarray,
    center: tuple[int, int],
    angle_deg: float,
) -> tuple[np.ndarray, tuple[int, int]]:
    height, width = img.shape[:2]
    rot_mat = cv2.getRotationMatrix2D((float(center[0]), float(center[1])), angle_deg, 1.0)
    rotated = cv2.warpAffine(
        img,
        rot_mat,
        (width, height),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0,
    )
    rotated_head = np.dot(rot_mat, np.array([center[0], center[1], 1])).astype(int)
    return rotated, (int(rotated_head[0]), int(rotated_head[1]))


def _draw_reference(img: np.ndarray, center: tuple[int, int]) -> np.ndarray:
    height, width = img.shape[:2]
    color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.line(color, (0, center[1]), (width, center[1]), (0, 255, 0), 2)
    cv2.circle(color, center, 8, (0, 0, 255), -1)
    cv2.circle(color, center, 4, (255, 255, 255), -1)
    return color
