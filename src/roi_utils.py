import cv2


def center_crop_lower_region(image, crop_ratio=0.55):
    """
    Automatic lower-region crop.
    This is a simple ROI helper for lower eyelid/conjunctiva area.
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


def resize_roi(image, size=224):
    """
    Resize ROI image to model input size.
    """
    return cv2.resize(image, (size, size))


def make_roi_preview(image):
    """
    Create ROI preview image using automatic lower-region crop.
    """
    roi = center_crop_lower_region(image)
    if roi is None:
        return None
    roi = resize_roi(roi, size=224)
    return roi