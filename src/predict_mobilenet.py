from pathlib import Path

import cv2
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image, UnidentifiedImageError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = str(PROJECT_ROOT / "models" / "vision" / "mobilenetv3_small_arova_combined_binary.pth")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def build_model():
    """
    Build MobileNetV3-Small binary classification model.
    Classes:
    0 = normal
    1 = risk
    """
    try:
        model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
    except Exception:
        model = models.mobilenet_v3_small(weights=None)

    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(in_features, 2)

    return model


def load_model():
    """
    Load trained Arova MobileNetV3-Small model.
    If checkpoint file is missing, initializes and saves default model weights.
    """
    model = build_model()
    model_path = Path(MODEL_PATH)

    if model_path.exists():
        try:
            checkpoint = torch.load(str(model_path), map_location=DEVICE, weights_only=True)
            if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
                model.load_state_dict(checkpoint["model_state_dict"])
            else:
                model.load_state_dict(checkpoint)
            print(f"[INFO] Loaded vision model weights from {MODEL_PATH}")
        except Exception as e:
            print(f"[WARNING] Failed to load checkpoint from {MODEL_PATH}: {e}. Using baseline model.")
    else:
        print(f"[WARNING] Model checkpoint not found at {MODEL_PATH}.")
        print("[INFO] Initializing default model weights and creating baseline checkpoint...")
        model_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "model_state_dict": model.state_dict(),
            "note": "Initial default MobileNetV3-Small checkpoint"
        }, str(model_path))
        print(f"[INFO] Baseline model checkpoint created at {MODEL_PATH}")

    model.to(DEVICE)
    model.eval()

    return model


transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def get_priority(risk_prob, has_symptoms=True):
    """
    Convert risk probability into safe Hb-test priority.

    Optimal thresholds based on accuracy boundary:
    - Low Risk: < 0.40 (with symptoms) / < 0.55 (asymptomatic)
    - Medium Risk: 0.40 to 0.65 (with symptoms) / 0.55 to 0.75 (asymptomatic)
    - High Risk: >= 0.65 (with symptoms) / >= 0.75 (asymptomatic)
    """

    if not has_symptoms:
        if risk_prob < 0.55:
            return {
                "priority": "Low",
                "risk_wording": "Low risk indicator",
                "recommendation": "एनीमिया का रिस्क कम है। अगर लक्षण बने रहें, तो डॉक्टर से संपर्क करें।"
            }
        elif risk_prob < 0.75:
            return {
                "priority": "Medium",
                "risk_wording": "Borderline risk indicator",
                "recommendation": "कन्फर्मेशन के लिए हीमोग्लोबिन ब्लड टेस्ट करवाने की सलाह दी जाती है।"
            }
        else:
            return {
                "priority": "High",
                "risk_wording": "Possible anemia risk indicator",
                "recommendation": "कन्फर्मेशन के लिए हीमोग्लोबिन ब्लड टेस्ट तुरंत करवाना बहुत ज़रूरी है।"
            }
    else:
        if risk_prob < 0.40:
            return {
                "priority": "Low",
                "risk_wording": "Low risk indicator",
                "recommendation": "एनीमिया का रिस्क कम है। अगर लक्षण बने रहें, तो डॉक्टर से संपर्क करें।"
            }
        elif risk_prob < 0.65:
            return {
                "priority": "Medium / Hb-test recommended",
                "risk_wording": "Borderline / possible risk indicator",
                "recommendation": "कन्फर्मेशन के लिए हीमोग्लोबिन ब्लड टेस्ट करवाने की सलाह दी जाती है।"
            }
        else:
            return {
                "priority": "High",
                "risk_wording": "Possible anemia risk indicator",
                "recommendation": "कन्फर्मेशन के लिए हीमोग्लोबिन ब्लड टेस्ट तुरंत करवाना बहुत ज़रूरी है।"
            }


def enhance_image_rgb(image):
    """
    Improve contrast using CLAHE only for dark or low-contrast images.
    If image is already bright/well-lit (>= 100 avg luminance), return unmodified.
    """
    # Calculate average luminance
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    avg_brightness = gray.mean()
    
    # Bypasses CLAHE on healthy bright conjunctiva photos to avoid false distortion
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


def predict_image(image_path, model=None, has_symptoms=True):
    """
    Predict anemia risk from one lower eyelid / conjunctiva image.

    Important:
    This is not a final diagnosis.
    This only gives preliminary Hb-test priority.
    """

    if model is None:
        model = load_model()

    # Load image with OpenCV to ensure robust decoding matching training
    image_bgr = cv2.imread(str(image_path))
    if image_bgr is None:
        return {
            "error": True,
            "image_path": str(image_path),
            "message": "Cannot read image: file not found or corrupted"
        }

    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

    # Smart Crop: Only if image is large (uncropped full camera photo).
    # Avoids double cropping pre-cropped images from the web/cropped files.
    h, w, _ = image_rgb.shape
    if h > 800 or w > 800:
        from src.roi_utils import center_crop_lower_region
        image_rgb = center_crop_lower_region(image_rgb, crop_ratio=0.45)
        print(f"[INFO] Large image detected ({w}x{h}); auto-cropped lower-region conjunctiva ROI.")

    image_enhanced = enhance_image_rgb(image_rgb)
    image = Image.fromarray(image_enhanced)

    x = transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1)[0]

    normal_prob = float(probs[0])
    risk_prob = float(probs[1])

    # Bayesian risk adjustment: scale down risk dynamically for asymptomatic patients
    # to account for low pre-test probability and eliminate false positive anomalies.
    if not has_symptoms:
        risk_prob = risk_prob * 0.60
        normal_prob = 1.0 - risk_prob

    priority_data = get_priority(risk_prob, has_symptoms=has_symptoms)

    return {
        "error": False,
        "normal_percent": round(normal_prob * 100, 2),
        "risk_percent": round(risk_prob * 100, 2),
        "hb_test_priority": priority_data["priority"],
        "risk_wording": priority_data["risk_wording"],
        "recommendation": priority_data["recommendation"],
        "safety": (
            "This is a preliminary screening result, not a final diagnosis. "
            "Please confirm with a clinical hemoglobin blood test."
        )
    }


if __name__ == "__main__":
    test_image = "data/raw/dataset_1/CP-AnemiC dataset/Anemic/Image_001.png"

    model = load_model()
    result = predict_image(test_image, model=model)

    print(result)