from pathlib import Path
import cv2
import pandas as pd
from tqdm import tqdm

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms

from sklearn.metrics import classification_report, confusion_matrix


ROOT_DIR = Path(__file__).resolve().parents[1]

TRAIN_CSV = ROOT_DIR / "data" / "labels" / "binary" / "combined" / "train.csv"
VAL_CSV = ROOT_DIR / "data" / "labels" / "binary" / "combined" / "val.csv"

MODEL_SAVE_PATH = ROOT_DIR / "models" / "vision" / "mobilenetv3_small_arova_combined_binary.pth"

IMAGE_SIZE = 224
BATCH_SIZE = 16
EPOCHS = 10
LEARNING_RATE = 1e-4

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


class ArovaBinaryDataset(Dataset):
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


def build_transform(train=True):
    if train:
        return transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=8),
            transforms.ColorJitter(
                brightness=0.15,
                contrast=0.15,
                saturation=0.10
            ),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

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
    model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)

    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(in_features, num_classes)

    return model


def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in tqdm(loader, desc="Training"):
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)

        _, preds = torch.max(outputs, 1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)

    epoch_loss = running_loss / total
    epoch_acc = correct / total

    return epoch_loss, epoch_acc


def evaluate(model, loader, criterion, device):
    model.eval()

    running_loss = 0.0
    correct = 0
    total = 0

    all_labels = []
    all_preds = []

    with torch.no_grad():
        for images, labels in tqdm(loader, desc="Validation"):
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)

            _, preds = torch.max(outputs, 1)

            correct += (preds == labels).sum().item()
            total += labels.size(0)

            all_labels.extend(labels.cpu().numpy())
            all_preds.extend(preds.cpu().numpy())

    epoch_loss = running_loss / total
    epoch_acc = correct / total

    return epoch_loss, epoch_acc, all_labels, all_preds


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("Device:", device)

    train_dataset = ArovaBinaryDataset(
        csv_path=TRAIN_CSV,
        transform=build_transform(train=True)
    )

    val_dataset = ArovaBinaryDataset(
        csv_path=VAL_CSV,
        transform=build_transform(train=False)
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0
    )

    print("\nTrain size:", len(train_dataset))
    print("Validation size:", len(val_dataset))

    print("\nTrain class balance:")
    print(train_dataset.df["label"].value_counts())

    print("\nValidation class balance:")
    print(val_dataset.df["label"].value_counts())

    model = build_model(num_classes=2)
    model = model.to(device)

    # Slight class weighting because risk/normal balance is not exactly equal
    train_counts = train_dataset.df["label"].value_counts()
    normal_count = train_counts.get("normal", 1)
    risk_count = train_counts.get("risk", 1)

    total = normal_count + risk_count
    normal_weight = total / (2 * normal_count)
    risk_weight = total / (2 * risk_count)

    class_weights = torch.tensor(
        [normal_weight, risk_weight],
        dtype=torch.float32
    ).to(device)

    print("\nClass weights:")
    print("normal:", normal_weight)
    print("risk:", risk_weight)

    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    best_val_acc = 0.0

    for epoch in range(EPOCHS):
        print("\n" + "=" * 70)
        print(f"Epoch {epoch + 1}/{EPOCHS}")
        print("=" * 70)

        train_loss, train_acc = train_one_epoch(
            model,
            train_loader,
            criterion,
            optimizer,
            device
        )

        val_loss, val_acc, val_labels, val_preds = evaluate(
            model,
            val_loader,
            criterion,
            device
        )

        print(f"\nTrain Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f}")
        print(f"Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.4f}")

        print("\nValidation Report:")
        print(classification_report(
            val_labels,
            val_preds,
            target_names=["normal", "risk"],
            zero_division=0
        ))

        print("Confusion Matrix:")
        print(confusion_matrix(val_labels, val_preds))

        if val_acc > best_val_acc:
            best_val_acc = val_acc

            MODEL_SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)

            torch.save({
                "model_state_dict": model.state_dict(),
                "label_to_idx": LABEL_TO_IDX,
                "idx_to_label": IDX_TO_LABEL,
                "image_size": IMAGE_SIZE,
                "best_val_acc": best_val_acc,
                "train_csv": str(TRAIN_CSV),
                "val_csv": str(VAL_CSV)
            }, MODEL_SAVE_PATH)

            print("\nBest model saved ✅")
            print("Path:", MODEL_SAVE_PATH)
            print("Best Val Acc:", best_val_acc)

    print("\nTraining complete ✅")
    print("Best Validation Accuracy:", best_val_acc)


if __name__ == "__main__":
    main()