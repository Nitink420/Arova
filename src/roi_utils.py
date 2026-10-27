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


def sclera_white_balance_calibration(image_rgb):
    """
    Sclera-Referenced Ambient Lighting Color Calibration.

    Uses the eye sclera (natural white reference) to calibrate color temperature,
    neutralizing yellow room lights, blue overcast shadows, or camera flash glare.

    Returns:
        calibrated_rgb (np.ndarray), calibration_metadata (dict)
    """
    if image_rgb is None or image_rgb.size == 0:
        return image_rgb, {"calibrated": False, "reason": "Empty image"}

    import numpy as np

    h, w = image_rgb.shape[:2]
    # Look for sclera in upper 65% of the frame (above conjunctiva)
    upper_h = int(h * 0.65)
    upper_region = image_rgb[:upper_h, :]

    hsv = cv2.cvtColor(upper_region, cv2.COLOR_RGB2HSV)
    # Sclera mask: High brightness (V >= 140), low saturation (S <= 45)
    sclera_mask = (hsv[:, :, 2] >= 140) & (hsv[:, :, 1] <= 45)
    sclera_pixels = upper_region[sclera_mask]

    if len(sclera_pixels) < 60:
        # Not enough clear sclera pixels detected, return uncalibrated
        return image_rgb, {"calibrated": False, "reason": "Insufficient sclera reference pixels"}

    # Compute mean R, G, B in sclera reference area
    mean_r = float(np.mean(sclera_pixels[:, 0]))
    mean_g = float(np.mean(sclera_pixels[:, 1]))
    mean_b = float(np.mean(sclera_pixels[:, 2]))

    max_val = max(mean_r, mean_g, mean_b, 1.0)
    # Gentle gain limits to prevent over-correction
    gain_r = float(np.clip(max_val / (mean_r + 1e-4), 0.82, 1.25))
    gain_g = float(np.clip(max_val / (mean_g + 1e-4), 0.82, 1.25))
    gain_b = float(np.clip(max_val / (mean_b + 1e-4), 0.82, 1.25))

    # Apply gains to entire RGB image
    calibrated = image_rgb.astype(np.float32)
    calibrated[:, :, 0] *= gain_r
    calibrated[:, :, 1] *= gain_g
    calibrated[:, :, 2] *= gain_b
    calibrated = np.clip(calibrated, 0, 255).astype(np.uint8)

    meta = {
        "calibrated": True,
        "sclera_pixels_count": int(len(sclera_pixels)),
        "gains": {"R": round(gain_r, 3), "G": round(gain_g, 3), "B": round(gain_b, 3)},
        "note": "Ambient lighting color-normalized against patient's sclera."
    }
    return calibrated, meta


def compute_erythema_index(image_rgb):
    """
    Computes clinical Erythema Index (EI):
    EI = log10(R) - log10(G)

    Measures hemoglobin vascularity / redness of conjunctival tissue.
    Lower EI indicates pallor (anemia risk).
    """
    if image_rgb is None or image_rgb.size == 0:
        return 0.0

    import numpy as np
    r = image_rgb[:, :, 0].astype(np.float32) + 1.0
    g = image_rgb[:, :, 1].astype(np.float32) + 1.0

    ei = np.log10(r) - np.log10(g)
    return float(round(float(np.mean(ei)), 4))