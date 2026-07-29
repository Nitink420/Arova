from pathlib import Path

import cv2
import pandas as pd
import numpy as np


IMAGE_SIZE = 224

TRAIN_CSV = Path("data/labels/train.csv")
VAL_CSV = Path("data/labels/val.csv")
TEST_CSV = Path("data/labels/test.csv")

OUTPUT_DIR = Path("data/processed/samples")


def read_image(image_path):
    """
    Read an image from disk and convert it from BGR to RGB.
    OpenCV reads images in BGR format by default.
    """
    image = cv2.imread(str(image_path))

    if image is None:
        return None

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


def resize_image(image, size=IMAGE_SIZE):
    """
    Resize the image to a fixed size.
    MobileNetV3 commonly uses 224x224 input images.
    """
    return cv2.resize(image, (size, size))


def normalize_image(image):
    """
    Scale pixel values from 0-255 to 0-1.
    This makes the image easier for the model to learn from.
    """
    return image.astype(np.float32) / 255.0


def blur_score(image):
    """
    Calculate a simple blur score.
    A very low score usually means the image is blurry.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    score = cv2.Laplacian(gray, cv2.CV_64F).var()
    return score


def brightness_score(image):
    """
    Calculate the average brightness of the image.
    Low value means dark image, high value means very bright image.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    score = gray.mean()
    return score


def enhance_image(image):
    """
    Improve contrast and brightness using CLAHE.

    CLAHE helps reveal details in dark or low-contrast images
    without changing the whole image too aggressively.
    """
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)

    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced_l = clahe.apply(l_channel)

    enhanced_lab = cv2.merge(
        (enhanced_l, a_channel, b_channel)
    )

    enhanced_rgb = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)

    return enhanced_rgb


def check_image_quality(image):
    """
    Check basic image quality using blur and brightness.
    This is not a medical check, only an image quality check.
    """
    blur = blur_score(image)
    brightness = brightness_score(image)

    is_blurry = blur < 50
    is_too_dark = brightness < 40
    is_too_bright = brightness > 220

    quality_status = "good"

    if is_blurry:
        quality_status = "blurry"
    elif is_too_dark:
        quality_status = "too_dark"
    elif is_too_bright:
        quality_status = "too_bright"

    return {
        "blur_score": blur,
        "brightness_score": brightness,
        "quality_status": quality_status
    }


def save_rgb_image(image, save_path):
    """
    Save an RGB image using OpenCV.
    OpenCV expects BGR format while saving, so we convert it back.
    """
    save_path.parent.mkdir(parents=True, exist_ok=True)

    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(save_path), image_bgr)


def audit_split(csv_path, split_name, sample_count=5):
    """
    Check a small number of images from one split.
    It prints image quality, resize result, normalization range,
    and saves original/enhanced sample images.
    """
    print("\n" + "=" * 70)
    print(f"{split_name.upper()} PREPROCESSING CHECK")
    print("=" * 70)

    if not csv_path.exists():
        print(f"ERROR: CSV not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)

    print(f"CSV path: {csv_path}")
    print(f"Total rows: {len(df)}")

    print("\nClass balance:")
    print(df["label"].value_counts())

    missing_images = 0
    unreadable_images = 0

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for index, row in df.head(sample_count).iterrows():
        image_path = Path(row["image_path"])

        print("\n" + "-" * 70)
        print("Image:", image_path)
        print("Label:", row["label"])

        if not image_path.exists():
            print("Status: missing")
            missing_images += 1
            continue

        image = read_image(image_path)

        if image is None:
            print("Status: unreadable")
            unreadable_images += 1
            continue

        h, w, c = image.shape
        print(f"Original size: width={w}, height={h}, channels={c}")

        original_quality = check_image_quality(image)

        print("\nOriginal quality:")
        print(f"Blur score: {original_quality['blur_score']:.2f}")
        print(f"Brightness score: {original_quality['brightness_score']:.2f}")
        print(f"Quality status: {original_quality['quality_status']}")

        enhanced = enhance_image(image)
        enhanced_quality = check_image_quality(enhanced)

        print("\nEnhanced quality:")
        print(f"Blur score: {enhanced_quality['blur_score']:.2f}")
        print(f"Brightness score: {enhanced_quality['brightness_score']:.2f}")
        print(f"Quality status: {enhanced_quality['quality_status']}")

        resized = resize_image(enhanced)
        normalized = normalize_image(resized)

        print("\nProcessed image:")
        print(f"Resized shape: {resized.shape}")
        print(f"Normalized min: {normalized.min():.3f}")
        print(f"Normalized max: {normalized.max():.3f}")

        original_save_path = OUTPUT_DIR / f"{split_name}_original_sample_{index}.png"
        enhanced_save_path = OUTPUT_DIR / f"{split_name}_enhanced_sample_{index}.png"

        save_rgb_image(image, original_save_path)
        save_rgb_image(resized, enhanced_save_path)

        print(f"Saved original sample: {original_save_path}")
        print(f"Saved enhanced sample: {enhanced_save_path}")

    print("\nSummary:")
    print(f"Missing images in checked samples: {missing_images}")
    print(f"Unreadable images in checked samples: {unreadable_images}")


def main():
    audit_split(TRAIN_CSV, "train")
    audit_split(VAL_CSV, "val")
    audit_split(TEST_CSV, "test")

    print("\nPreprocessing check complete!")
    print("\nTraining pipeline:")
    print("Read image -> CLAHE enhance -> Resize 224x224 -> Normalize 0-1")


if __name__ == "__main__":
    main()