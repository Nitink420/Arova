from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split


INPUT_CSV = Path("data/labels/dataset_1_labels.csv")
OUTPUT_DIR = Path("data/labels")

TRAIN_CSV = OUTPUT_DIR / "train.csv"
VAL_CSV = OUTPUT_DIR / "val.csv"
TEST_CSV = OUTPUT_DIR / "test.csv"


def main():
    if not INPUT_CSV.exists():
        print(f"ERROR: Input CSV not found: {INPUT_CSV}")
        return

    df = pd.read_csv(INPUT_CSV)

    print("Original dataset shape:", df.shape)
    print("\nOriginal class balance:")
    print(df["label"].value_counts())

    # Step 1: Train = 70%, temp = 30%
    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        random_state=42,
        stratify=df["label"]
    )

    # Step 2: temp ko half-half split karo
    # val = 15%, test = 15%
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=42,
        stratify=temp_df["label"]
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    train_df.to_csv(TRAIN_CSV, index=False)
    val_df.to_csv(VAL_CSV, index=False)
    test_df.to_csv(TEST_CSV, index=False)

    print("\nSplits created successfully!")

    print(f"\nTrain saved at: {TRAIN_CSV}")
    print("Train shape:", train_df.shape)
    print(train_df["label"].value_counts())

    print(f"\nValidation saved at: {VAL_CSV}")
    print("Validation shape:", val_df.shape)
    print(val_df["label"].value_counts())

    print(f"\nTest saved at: {TEST_CSV}")
    print("Test shape:", test_df.shape)
    print(test_df["label"].value_counts())


if __name__ == "__main__":
    main()