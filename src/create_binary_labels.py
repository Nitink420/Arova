from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split


INPUT_CSV = Path("data/labels/dataset_1_labels.csv")
OUTPUT_DIR = Path("data/labels/binary")

BINARY_LABELS_CSV = OUTPUT_DIR / "dataset_1_binary_labels.csv"
TRAIN_CSV = OUTPUT_DIR / "train.csv"
VAL_CSV = OUTPUT_DIR / "val.csv"
TEST_CSV = OUTPUT_DIR / "test.csv"


def make_binary_label(label):
    label = str(label).strip().lower()

    if label == "normal":
        return "normal"

    return "risk"


def main():
    if not INPUT_CSV.exists():
        print(f"ERROR: Input CSV not found: {INPUT_CSV}")
        return

    df = pd.read_csv(INPUT_CSV)

    df["binary_label"] = df["label"].apply(make_binary_label)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df.to_csv(BINARY_LABELS_CSV, index=False)

    print("Binary labels created.")
    print(f"Saved at: {BINARY_LABELS_CSV}")
    print("\nBinary class balance:")
    print(df["binary_label"].value_counts())

    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        random_state=42,
        stratify=df["binary_label"]
    )

    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=42,
        stratify=temp_df["binary_label"]
    )

    train_df.to_csv(TRAIN_CSV, index=False)
    val_df.to_csv(VAL_CSV, index=False)
    test_df.to_csv(TEST_CSV, index=False)

    print("\nBinary splits created successfully!")

    print("\nTrain:")
    print(train_df["binary_label"].value_counts())

    print("\nValidation:")
    print(val_df["binary_label"].value_counts())

    print("\nTest:")
    print(test_df["binary_label"].value_counts())


if __name__ == "__main__":
    main()