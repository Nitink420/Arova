from pathlib import Path
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]

DATASET2_DIR = ROOT_DIR / "data" / "raw" / "dataset_2" / "DS-anemia"
OUTPUT_DIR = ROOT_DIR / "data" / "labels" / "binary"
OUTPUT_PATH = OUTPUT_DIR / "dataset_2_binary_labels.csv"

# MVP rule:
# Hgb < 12.0  => risk
# Hgb >= 12.0 => normal
# This is for research/demo screening only, not diagnosis.
HGB_THRESHOLD = 12.0

IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp"]


def get_label_from_hgb(hgb):
    if pd.isna(hgb):
        return None

    try:
        hgb = float(hgb)
    except ValueError:
        return None

    if hgb < HGB_THRESHOLD:
        return "risk"

    return "normal"


def find_images_for_patient(country_dir, patient_number):
    """
    Dataset 2 structure is like:
    India/
      India.xlsx
      1/
      2/
      ...
    Italy/
      Italy.xlsx
      1/
      2/
      ...

    This function finds all image files inside patient folder.
    """
    patient_dir = country_dir / str(int(patient_number))

    if not patient_dir.exists():
        return []

    image_paths = []

    for ext in IMAGE_EXTENSIONS:
        image_paths.extend(patient_dir.rglob(f"*{ext}"))
        image_paths.extend(patient_dir.rglob(f"*{ext.upper()}"))

    return image_paths


def process_country(country_name, excel_name):
    country_dir = DATASET2_DIR / country_name
    excel_path = country_dir / excel_name

    if not excel_path.exists():
        raise FileNotFoundError(f"Excel not found: {excel_path}")

    df = pd.read_excel(excel_path)

    # Remove unnamed empty columns
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]

    records = []

    for _, row in df.iterrows():
        patient_number = row.get("Number")
        hgb = row.get("Hgb")
        gender = row.get("Gender")
        age = row.get("Age")
        note = row.get("Note")

        label = get_label_from_hgb(hgb)

        if label is None:
            continue

        image_paths = find_images_for_patient(country_dir, patient_number)

        for image_path in image_paths:
            rel_path = image_path.relative_to(ROOT_DIR).as_posix()

            records.append({
                "image_path": rel_path,
                "dataset": "dataset_2",
                "country": country_name,
                "patient_number": int(patient_number),
                "hgb": float(hgb),
                "gender": gender,
                "age": age,
                "note": note,
                "label": label
            })

    return records


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_records = []

    all_records.extend(process_country("India", "India.xlsx"))
    all_records.extend(process_country("Italy", "Italy.xlsx"))

    labels_df = pd.DataFrame(all_records)

    if labels_df.empty:
        print("No records created. Please check Dataset 2 folder structure.")
        return

    labels_df.to_csv(OUTPUT_PATH, index=False)

    print("\nDataset 2 binary labels created ✅")
    print(f"Saved to: {OUTPUT_PATH}")

    print("\nTotal images:")
    print(len(labels_df))

    print("\nClass balance:")
    print(labels_df["label"].value_counts())

    print("\nCountry balance:")
    print(labels_df["country"].value_counts())

    print("\nSample rows:")
    print(labels_df.head())


if __name__ == "__main__":
    main()