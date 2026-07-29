from pathlib import Path
import argparse

import cv2
import torch
import torch.nn as nn
from torchvision import models, transforms


IMAGE_SIZE = 224
MODEL_PATH = Path("models/vision/mobilenetv3_small_arova_binary.pth")
RISK_THRESHOLD = 0.35

ID_TO_LABEL = {
    0: "normal",
    1: "risk"
}


def read_image(image_path):
    """Read image from disk and convert BGR to RGB."""
    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


def enhance_image(image):
    """Improve contrast using CLAHE for dark or low-contrast images."""
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced_l = clahe.apply(l_channel)
    enhanced_lab = cv2.merge((enhanced_l, a_channel, b_channel))
    enhanced_rgb = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)

    return enhanced_rgb


def build_transform():
    """Create image transform for prediction."""
    return transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])


def build_model(num_classes=2):
    """Create MobileNetV3-Small model with binary output."""
    model = models.mobilenet_v3_small(weights=None)

    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(in_features, num_classes)

    return model


def load_model(device):
    """Load trained Arova binary model."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

    checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=True)

    model = build_model(num_classes=2)
    model.load_state_dict(checkpoint["model_state_dict"])
    model = model.to(device)
    model.eval()

    return model


def predict_image(image_path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = load_model(device)
    transform = build_transform()

    image = read_image(image_path)
    enhanced = enhance_image(image)

    input_tensor = transform(enhanced)
    input_tensor = input_tensor.unsqueeze(0).to(device)

    softmax = nn.Softmax(dim=1)

    with torch.no_grad():
        outputs = model(input_tensor)
        probs = softmax(outputs)

    normal_prob = float(probs[0][0].cpu().item())
    risk_prob = float(probs[0][1].cpu().item())

    if risk_prob >= RISK_THRESHOLD:
        prediction = "risk"
        message = "Anemia risk detected. Please confirm with a clinical hemoglobin blood test."
    else:
        prediction = "normal"
        message = "Low anemia risk detected. If symptoms are present, please still confirm with a clinical hemoglobin blood test."

    print("\n" + "=" * 70)
    print("AROVA SCREENING RESULT")
    print("=" * 70)

    print(f"Image path: {image_path}")
    print(f"Prediction: {prediction}")
    print(f"Normal probability: {normal_prob:.4f}")
    print(f"Risk probability: {risk_prob:.4f}")
    print(f"Risk threshold: {RISK_THRESHOLD}")

    print("\nRecommendation:")
    print(message)

    print("\nSafety note:")
    print(
        "This is a preliminary screening result, not a final diagnosis. "
        "Please confirm with a clinical hemoglobin blood test."
    )


def main():
    parser = argparse.ArgumentParser(description="Arova binary prediction script")

    parser.add_argument(
        "--image_path",
        type=str,
        required=True,
        help="Path to eye/conjunctiva image"
    )

    args = parser.parse_args()

    predict_image(args.image_path)


if __name__ == "__main__":
    main()