from pathlib import Path
import pandas as pd


DATASET_1_DIR = Path("data/raw/dataset_1")
OUTPUT_CSV = Path("data/labels/dataset_1_labels.csv")


def normalize_severity(value):
    value = str(value).strip().lower()

    if "non" in value:
        return "normal"
    if "mild" in value:
        return "mild"
    if "moderate" in value:
        return "moderate"
    if "severe" in value:
        return "severe"

    return "unknown"


def main():
    excel_files = list(DATASET_1_DIR.rglob("*.xlsx"))

    if not excel_files:
        print("ERROR: No Excel file found in dataset_1")
        return

    excel_path = excel_files[0]
    print(f"Reading Excel file: {excel_path}")

    df = pd.read_excel(excel_path)

    required_columns = ["IMAGE_ID", "HB_LEVEL", "Severity"]

    for col in required_columns:
        if col not in df.columns:
            print(f"ERROR: Missing column: {col}")
            return

    image_files = list(DATASET_1_DIR.rglob("*.png"))

    image_map = {}
    for image_path in image_files:
        image_id = image_path.stem
        image_map[image_id] = image_path

    rows = []

    for _, row in df.iterrows():
        image_id = str(row["IMAGE_ID"]).strip()
        hb_level = row["HB_LEVEL"]
        severity = row["Severity"]

        if image_id not in image_map:
            print(f"WARNING: Image not found for {image_id}")
            continue

        label = normalize_severity(severity)

        rows.append({
            "image_path": str(image_map[image_id]),
            "image_id": image_id,
            "hb_level": hb_level,
            "severity": severity,
            "label": label
        })

    output_df = pd.DataFrame(rows)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(OUTPUT_CSV, index=False)

    print("\nLabel CSV created successfully!")
    print(f"Saved at: {OUTPUT_CSV}")
    print(f"Total rows: {len(output_df)}")

    print("\nClass balance:")
    print(output_df["label"].value_counts())


if __name__ == "__main__":
    main()