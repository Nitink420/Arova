from pathlib import Path
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]

INPUT_PATH = ROOT_DIR / "data" / "labels" / "binary" / "dataset_2_binary_labels.csv"
OUTPUT_PATH = ROOT_DIR / "data" / "labels" / "binary" / "dataset_2_binary_labels_filtered.csv"


def main():
    df = pd.read_csv(INPUT_PATH)

    print("\nBefore cleaning:")
    print("Total rows:", len(df))
    print(df["label"].value_counts())

    # Step 1: remove exact duplicate image paths
    df = df.drop_duplicates(subset=["image_path"]).copy()

    print("\nAfter removing duplicate image paths:")
    print("Total rows:", len(df))
    print(df["label"].value_counts())

    # Step 2: keep only forniceal_palpebral images
    # These are closer to useful conjunctiva region.
    filtered_df = df[
        df["image_path"]
        .astype(str)
        .str.lower()
        .str.contains("forniceal_palpebral")
    ].copy()

    print("\nAfter keeping only forniceal_palpebral images:")
    print("Total rows:", len(filtered_df))
    print(filtered_df["label"].value_counts())

    print("\nCountry balance:")
    print(filtered_df["country"].value_counts())

    print("\nPatient count:")
    patient_count = filtered_df[["country", "patient_number"]].drop_duplicates().shape[0]
    print(patient_count)

    print("\nSample rows:")
    print(filtered_df.head())

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    filtered_df.to_csv(OUTPUT_PATH, index=False)

    print("\nFiltered Dataset 2 labels saved ✅")
    print("Saved to:", OUTPUT_PATH)


if __name__ == "__main__":
    main()