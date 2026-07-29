from pathlib import Path
import cv2
import pandas as pd
import numpy as np

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms

from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


ROOT_DIR = Path(__file__).resolve().parents[1]

TEST_CSV = ROOT_DIR / "data" / "labels" / "binary" / "combined" / "test.csv"
MODEL_PATH = ROOT_DIR / "models" / "vision" / "mobilenetv3_small_arova_combined_binary.pth"

IMAGE_SIZE = 224
BATCH_SIZE = 16

LABEL_TO_IDX = {
    "normal": 0,
    "risk": 1
}

IDX_TO_LABEL = {
    0: "normal",
    1: "risk"
}


def enhance_image_rgb(image):
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


class ArovaTestDataset(Dataset):
    def __init__(self, csv_path, transform=None):
        self.df = pd.read_csv(csv_path)
        self.transform = transform

        self.df["label"] = self.df["label"].astype(str).str.lower().str.strip()
        self.df = self.df[self.df["label"].isin(LABEL_TO_IDX.keys())].reset_index(drop=True)

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]

        image_path = ROOT_DIR / row["image_path"]
        label_name = row["label"]
        label = LABEL_TO_IDX[label_name]

        image_bgr = cv2.imread(str(image_path))

        if image_bgr is None:
            raise ValueError(f"Could not read image: {image_path}")

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        image_rgb = enhance_image_rgb(image_rgb)

        if self.transform:
            image_rgb = self.transform(image_rgb)

        return image_rgb, label


def build_transform():
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
    model = models.mobilenet_v3_small(weights=None)

    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(in_features, num_classes)

    return model


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("Device:", device)

    checkpoint = torch.load(MODEL_PATH, map_location=device, weights_only=True)

    model = build_model(num_classes=2)
    model.load_state_dict(checkpoint["model_state_dict"])
    model = model.to(device)
    model.eval()

    dataset = ArovaTestDataset(
        csv_path=TEST_CSV,
        transform=build_transform()
    )

    loader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0
    )

    print("\nTest size:", len(dataset))
    print("\nTest class balance:")
    print(dataset.df["label"].value_counts())

    softmax = nn.Softmax(dim=1)

    all_labels = []
    all_risk_probs = []

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)

            outputs = model(images)
            probs = softmax(outputs)

            risk_probs = probs[:, 1].cpu().numpy()

            all_risk_probs.extend(risk_probs)
            all_labels.extend(labels.numpy())

    all_labels = np.array(all_labels)
    all_risk_probs = np.array(all_risk_probs)

    thresholds = [0.50, 0.45, 0.40, 0.35, 0.30]

    print("\n" + "=" * 70)
    print("Threshold Comparison")
    print("=" * 70)

    for threshold in thresholds:
        preds = (all_risk_probs >= threshold).astype(int)

        acc = accuracy_score(all_labels, preds)
        cm = confusion_matrix(all_labels, preds)

        normal_total = cm[0].sum()
        risk_total = cm[1].sum()

        normal_correct = cm[0][0]
        risk_correct = cm[1][1]

        normal_recall = normal_correct / normal_total if normal_total else 0
        risk_recall = risk_correct / risk_total if risk_total else 0

        risk_missed = cm[1][0]

        print("\nThreshold:", threshold)
        print("Accuracy:", round(acc, 4))
        print("Normal recall:", round(normal_recall, 4))
        print("Risk recall:", round(risk_recall, 4))
        print("Risk missed:", risk_missed)
        print("Confusion Matrix:")
        print(cm)

        print("\nClassification Report:")
        print(classification_report(
            all_labels,
            preds,
            target_names=["normal", "risk"],
            zero_division=0
        ))


if __name__ == "__main__":
    main()