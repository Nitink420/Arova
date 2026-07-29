from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, classification_report
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from tqdm import tqdm


IMAGE_SIZE = 224
BATCH_SIZE = 16
EPOCHS = 10
LEARNING_RATE = 1e-4

TRAIN_CSV = Path("data/labels/train.csv")
VAL_CSV = Path("data/labels/val.csv")

MODEL_DIR = Path("models/vision")
MODEL_PATH = MODEL_DIR / "mobilenetv3_small_arova.pth"

LABEL_TO_ID = {
    "normal": 0,
    "mild": 1,
    "moderate": 2,
    "severe": 3
}

ID_TO_LABEL = {
    0: "normal",
    1: "mild",
    2: "moderate",
    3: "severe"
}


def read_image(image_path):
    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


def enhance_image(image):
    """
    Improve contrast using CLAHE.
    This helps with dark or low-contrast eye images.
    """
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


class ArovaDataset(Dataset):
    def __init__(self, csv_path, transform=None):
        self.df = pd.read_csv(csv_path)
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, index):
        row = self.df.iloc[index]

        image_path = Path(row["image_path"])
        label_name = row["label"]
        label_id = LABEL_TO_ID[label_name]

        image = read_image(image_path)
        image = enhance_image(image)

        if self.transform:
            image = self.transform(image)

        return image, torch.tensor(label_id, dtype=torch.long)


def build_transforms():
    train_transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=8),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    val_transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    return train_transform, val_transform


def calculate_class_weights(csv_path):
    df = pd.read_csv(csv_path)
    class_counts = df["label"].value_counts()

    total_samples = len(df)
    num_classes = len(LABEL_TO_ID)

    weights = []

    for label_name in LABEL_TO_ID.keys():
        count = class_counts[label_name]
        weight = total_samples / (num_classes * count)
        weights.append(weight)

    return torch.tensor(weights, dtype=torch.float32)


def build_model(num_classes=4):
    model = models.mobilenet_v3_small(
        weights=models.MobileNet_V3_Small_Weights.DEFAULT
    )

    in_features = model.classifier[3].in_features

    model.classifier[3] = nn.Linear(
        in_features,
        num_classes
    )

    return model


def train_one_epoch(model, dataloader, criterion, optimizer, device):
    model.train()

    running_loss = 0.0
    all_preds = []
    all_labels = []

    for images, labels in tqdm(dataloader, desc="Training"):
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()

        running_loss += loss.item()

        preds = torch.argmax(outputs, dim=1)

        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

    avg_loss = running_loss / len(dataloader)
    acc = accuracy_score(all_labels, all_preds)

    return avg_loss, acc


def validate(model, dataloader, criterion, device):
    model.eval()

    running_loss = 0.0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for images, labels in tqdm(dataloader, desc="Validation"):
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item()

            preds = torch.argmax(outputs, dim=1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    avg_loss = running_loss / len(dataloader)
    acc = accuracy_score(all_labels, all_preds)

    return avg_loss, acc, all_labels, all_preds


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    train_transform, val_transform = build_transforms()

    train_dataset = ArovaDataset(TRAIN_CSV, transform=train_transform)
    val_dataset = ArovaDataset(VAL_CSV, transform=val_transform)

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

    model = build_model(num_classes=4)
    model = model.to(device)

    class_weights = calculate_class_weights(TRAIN_CSV).to(device)
    print("Class weights:", class_weights)

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

        val_loss, val_acc, val_labels, val_preds = validate(
            model,
            val_loader,
            criterion,
            device
        )

        print(f"Train Loss: {train_loss:.4f}")
        print(f"Train Accuracy: {train_acc:.4f}")
        print(f"Val Loss: {val_loss:.4f}")
        print(f"Val Accuracy: {val_acc:.4f}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc

            MODEL_DIR.mkdir(parents=True, exist_ok=True)

            torch.save({
                "model_state_dict": model.state_dict(),
                "label_to_id": LABEL_TO_ID,
                "id_to_label": ID_TO_LABEL,
                "image_size": IMAGE_SIZE
            }, MODEL_PATH)

            print(f"Best model saved at: {MODEL_PATH}")

    print("\nTraining complete!")
    print(f"Best validation accuracy: {best_val_acc:.4f}")

    print("\nFinal validation report:")
    print(
        classification_report(
            val_labels,
            val_preds,
            target_names=[ID_TO_LABEL[i] for i in range(4)]
        )
    )

    print("\nSafety note:")
    print(
        "This is a preliminary screening result, not a final diagnosis. "
        "Please confirm with a clinical hemoglobin blood test."
    )


if __name__ == "__main__":
    main()