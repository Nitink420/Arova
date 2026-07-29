from pathlib import Path
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]

DATASET1_PATH = ROOT_DIR / "data" / "labels" / "binary" / "dataset_1_binary_labels.csv"
DATASET2_PATH = ROOT_DIR / "data" / "labels" / "binary" / "dataset_2_binary_labels_filtered.csv"

OUTPUT_PATH = ROOT_DIR / "data" / "labels" / "binary" / "combined_binary_labels.csv"


def main():
    if not DATASET1_PATH.exists():
        raise FileNotFoundError(f"Dataset 1 labels not found: {DATASET1_PATH}")

    if not DATASET2_PATH.exists():
        raise FileNotFoundError(f"Dataset 2 filtered labels not found: {DATASET2_PATH}")

    df1 = pd.read_csv(DATASET1_PATH)
    df2 = pd.read_csv(DATASET2_PATH)

    print("\nDataset 1 columns:")
    print(df1.columns.tolist())

    print("\nDataset 2 columns:")
    print(df2.columns.tolist())

    # Dataset 1 has original label + binary_label
    # For combined binary training, use binary_label only.
    if "binary_label" not in df1.columns:
        raise ValueError("Dataset 1 CSV must contain binary_label column.")

    df1_clean = pd.DataFrame({
        "image_path": df1["image_path"],
        "label": df1["binary_label"],
        "dataset": "dataset_1",
        "source_id": df1.get("image_id", "unknown"),
        "hgb": df1.get("hb_level", None),
        "country": "unknown",
        "age": None,
        "gender": None
    })

    df2_clean = pd.DataFrame({
        "image_path": df2["image_path"],
        "label": df2["label"],
        "dataset": "dataset_2",
        "source_id": df2["country"].astype(str) + "_" + df2["patient_number"].astype(str),
        "hgb": df2["hgb"],
        "country": df2["country"],
        "age": df2["age"],
        "gender": df2["gender"]
    })

    combined_df = pd.concat([df1_clean, df2_clean], ignore_index=True)

    # Normalize paths and labels
    combined_df["image_path"] = combined_df["image_path"].astype(str).str.replace("\\", "/", regex=False)
    combined_df["label"] = combined_df["label"].astype(str).str.lower().str.strip()

    # Keep only binary labels
    combined_df = combined_df[combined_df["label"].isin(["normal", "risk"])].copy()

    # Remove duplicate image paths
    combined_df = combined_df.drop_duplicates(subset=["image_path"]).copy()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    combined_df.to_csv(OUTPUT_PATH, index=False)

    print("\nCombined binary labels created ✅")
    print("Saved to:", OUTPUT_PATH)

    print("\nTotal rows:")
    print(len(combined_df))

    print("\nDataset balance:")
    print(combined_df["dataset"].value_counts())

    print("\nClass balance:")
    print(combined_df["label"].value_counts())

    print("\nClass balance by dataset:")
    print(pd.crosstab(combined_df["dataset"], combined_df["label"]))

    print("\nUnique labels:")
    print(combined_df["label"].unique())

    print("\nSample rows:")
    print(combined_df.head())


if __name__ == "__main__":
    main()