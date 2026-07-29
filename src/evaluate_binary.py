from pathlib import Path

import cv2
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from tqdm import tqdm


IMAGE_SIZE = 224
BATCH_SIZE = 16

TEST_CSV = Path("data/labels/binary/test.csv")
MODEL_PATH = Path("models/vision/mobilenetv3_small_arova_binary.pth")

LABEL_TO_ID = {
    "normal": 0,
    "risk": 1
}

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


class ArovaBinaryDataset(Dataset):
    """Dataset class for binary model evaluation."""

    def __init__(self, csv_path, transform=None):
        self.df = pd.read_csv(csv_path)
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, index):
        row = self.df.iloc[index]

        image_path = Path(row["image_path"])
        label_name = row["binary_label"]
        label_id = LABEL_TO_ID[label_name]

        image = read_image(image_path)
        image = enhance_image(image)

        if self.transform:
            image = self.transform(image)

        return image, torch.tensor(label_id, dtype=torch.long)


def build_transform():
    """Create image transform for evaluation."""
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


def evaluate(model, dataloader, device):
    """Run model on test data and collect predictions."""
    model.eval()

    all_labels = []
    all_default_preds = []
    all_risk_probs = []

    softmax = nn.Softmax(dim=1)

    with torch.no_grad():
        for images, labels in tqdm(dataloader, desc="Testing"):
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            probs = softmax(outputs)

            risk_probs = probs[:, 1]
            default_preds = torch.argmax(probs, dim=1)

            all_labels.extend(labels.cpu().numpy())
            all_default_preds.extend(default_preds.cpu().numpy())
            all_risk_probs.extend(risk_probs.cpu().numpy())

    return all_labels, all_default_preds, all_risk_probs


def print_metrics(labels, preds, title):
    """Print accuracy, report, and confusion matrix."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

    print("Accuracy:", accuracy_score(labels, preds))

    print("\nClassification report:")
    print(
        classification_report(
            labels,
            preds,
            target_names=["normal", "risk"]
        )
    )

    print("\nConfusion matrix:")
    print(confusion_matrix(labels, preds))


def evaluate_with_threshold(labels, risk_probs, threshold):
    """
    Convert risk probability to prediction using custom threshold.
    Lower threshold means the model flags more cases as risk.
    """
    preds = []

    for prob in risk_probs:
        if prob >= threshold:
            preds.append(1)
        else:
            preds.append(0)

    print_metrics(
        labels,
        preds,
        title=f"THRESHOLD EVALUATION | risk threshold = {threshold}"
    )


def main():
    if not TEST_CSV.exists():
        print(f"ERROR: Test CSV not found: {TEST_CSV}")
        return

    if not MODEL_PATH.exists():
        print(f"ERROR: Model not found: {MODEL_PATH}")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    transform = build_transform()
    test_dataset = ArovaBinaryDataset(TEST_CSV, transform=transform)

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0
    )

    checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=True)

    model = build_model(num_classes=2)
    model.load_state_dict(checkpoint["model_state_dict"])
    model = model.to(device)

    labels, default_preds, risk_probs = evaluate(model, test_loader, device)

    print_metrics(
        labels,
        default_preds,
        title="DEFAULT TEST EVALUATION"
    )

    evaluate_with_threshold(labels, risk_probs, threshold=0.50)
    evaluate_with_threshold(labels, risk_probs, threshold=0.45)
    evaluate_with_threshold(labels, risk_probs, threshold=0.40)
    evaluate_with_threshold(labels, risk_probs, threshold=0.35)

    print("\nSafety note:")
    print(
        "This is a preliminary screening result, not a final diagnosis. "
        "Please confirm with a clinical hemoglobin blood test."
    )


if __name__ == "__main__":
    main()