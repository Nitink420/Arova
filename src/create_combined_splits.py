from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split


ROOT_DIR = Path(__file__).resolve().parents[1]

INPUT_PATH = ROOT_DIR / "data" / "labels" / "binary" / "combined_binary_labels.csv"

OUTPUT_DIR = ROOT_DIR / "data" / "labels" / "binary" / "combined"
TRAIN_PATH = OUTPUT_DIR / "train.csv"
VAL_PATH = OUTPUT_DIR / "val.csv"
TEST_PATH = OUTPUT_DIR / "test.csv"

RANDOM_STATE = 42


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Combined labels file not found: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH)

    print("\nLoaded combined labels ✅")
    print("Total rows:", len(df))

    print("\nClass balance:")
    print(df["label"].value_counts())

    print("\nDataset balance:")
    print(df["dataset"].value_counts())

    # Safety check: only binary labels allowed
    allowed_labels = {"normal", "risk"}
    found_labels = set(df["label"].astype(str).str.lower().unique())

    if not found_labels.issubset(allowed_labels):
        raise ValueError(f"Unexpected labels found: {found_labels}")

    # Normalize labels
    df["label"] = df["label"].astype(str).str.lower().str.strip()

    # Group ID:
    # Dataset 1: source_id is image_id, mostly one image per source
    # Dataset 2: source_id is country_patientNumber, so patient-wise split happens
    df["group_id"] = df["dataset"].astype(str) + "_" + df["source_id"].astype(str)

    groups_df = df.groupby("group_id").agg({
        "label": "first",
        "dataset": "first"
    }).reset_index()

    print("\nTotal groups:")
    print(len(groups_df))

    print("\nGroup class balance:")
    print(groups_df["label"].value_counts())

    # 70% train, 15% validation, 15% test
    train_groups, temp_groups = train_test_split(
        groups_df,
        test_size=0.30,
        random_state=RANDOM_STATE,
        stratify=groups_df["label"]
    )

    val_groups, test_groups = train_test_split(
        temp_groups,
        test_size=0.50,
        random_state=RANDOM_STATE,
        stratify=temp_groups["label"]
    )

    train_df = df[df["group_id"].isin(train_groups["group_id"])].copy()
    val_df = df[df["group_id"].isin(val_groups["group_id"])].copy()
    test_df = df[df["group_id"].isin(test_groups["group_id"])].copy()

    # Remove helper column before saving
    train_df = train_df.drop(columns=["group_id"])
    val_df = val_df.drop(columns=["group_id"])
    test_df = test_df.drop(columns=["group_id"])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    train_df.to_csv(TRAIN_PATH, index=False)
    val_df.to_csv(VAL_PATH, index=False)
    test_df.to_csv(TEST_PATH, index=False)

    print("\nCombined splits created ✅")

    print("\nTrain:")
    print("Rows:", len(train_df))
    print(train_df["label"].value_counts())
    print("\nDataset balance:")
    print(train_df["dataset"].value_counts())

    print("\nValidation:")
    print("Rows:", len(val_df))
    print(val_df["label"].value_counts())
    print("\nDataset balance:")
    print(val_df["dataset"].value_counts())

    print("\nTest:")
    print("Rows:", len(test_df))
    print(test_df["label"].value_counts())
    print("\nDataset balance:")
    print(test_df["dataset"].value_counts())

    print("\nSaved files:")
    print(TRAIN_PATH)
    print(VAL_PATH)
    print(TEST_PATH)


if __name__ == "__main__":
    main()