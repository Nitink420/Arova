# app/utils/image_utils.py
"""
AROVA Image Processing Utilities

Provides image enhancement and ROI cropping functions used by VisionService.
Extracted from the original src/predict_mobilenet.py and src/roi_utils.py
for clean separation of concerns.
"""

import cv2
import numpy as np

from app.core.logger import get_logger

logger = get_logger(__name__)


def enhance_image_rgb(image: np.ndarray) -> np.ndarray:
    """
    Improve contrast using CLAHE only for dark or low-contrast images.

    If the image is already bright/well-lit (>= 100 avg luminance),
    returns the image unmodified to avoid false color distortion on
    healthy bright conjunctiva photos.

    Args:
        image: RGB image as numpy array (H, W, 3).

    Returns:
        Enhanced RGB image as numpy array.
    """
    if image is None:
        return image

    # Calculate average luminance
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    avg_brightness = gray.mean()

    # Bypass CLAHE on healthy bright conjunctiva photos
    if avg_brightness >= 100:
        return image

    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=1.5,
        tileGridSize=(8, 8)
    )

    enhanced_l = clahe.apply(l_channel)
    enhanced_lab = cv2.merge((enhanced_l, a_channel, b_channel))
    enhanced_rgb = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)

    return enhanced_rgb


def center_crop_lower_region(image: np.ndarray, crop_ratio: float = 0.55) -> np.ndarray:
    """
    Automatic lower-region crop for eyelid/conjunctiva ROI extraction.

    Crops the lower portion of a large image to isolate the conjunctiva area.
    Avoids double-cropping on already-cropped images from web/files.

    Args:
        image: Image as numpy array (BGR or RGB).
        crop_ratio: Fraction of height to keep from the bottom (default 0.55).

    Returns:
        Cropped image, or original if crop would be empty.
    """
    if image is None:
        return None

    # Handle grayscale images (2D arrays) — convert to 3-channel
    if image.ndim == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    if image.ndim != 3 or image.shape[2] < 3:
        return image

    h, w, _ = image.shape

    start_y = int(h * (1 - crop_ratio))
    end_y = h

    start_x = int(w * 0.10)
    end_x = int(w * 0.90)

    cropped = image[start_y:end_y, start_x:end_x]

    if cropped.size == 0:
        return image

    return cropped


def resize_roi(image: np.ndarray, size: int = 224) -> np.ndarray:
    """
    Resize ROI image to model input size.

    Args:
        image: Image as numpy array.
        size: Target size (square, default 224).

    Returns:
        Resized image.
    """
    return cv2.resize(image, (size, size))


def smart_crop_if_needed(image_rgb: np.ndarray) -> np.ndarray:
    """
    Apply ROI cropping only if the image is large (uncropped full camera photo).

    Avoids double-cropping on pre-cropped images from web/files.

    Args:
        image_rgb: RGB image as numpy array.

    Returns:
        Cropped image if large, or original image.
    """
    h, w = image_rgb.shape[:2]
    if h > 800 or w > 800:
        logger.info(
            "Large image detected (%dx%d); auto-cropping lower-region conjunctiva ROI.",
            w, h
        )
        return center_crop_lower_region(image_rgb, crop_ratio=0.45)
    return image_rgb
