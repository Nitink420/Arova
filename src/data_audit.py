from pathlib import Path
import argparse

import cv2
import pandas as pd


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}
TABLE_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def find_files(folder_path, extensions):
    folder_path = Path(folder_path)
    return [
        file_path
        for file_path in folder_path.rglob("*")
        if file_path.is_file() and file_path.suffix.lower() in extensions
    ]


def classify_image_type(image_path):
    name = image_path.name.lower()

    if "forniceal_palpebral" in name:
        return "forniceal_palpebral"
    if "palpebral" in name or "palplebral" in name or "papebral" in name:
        return "palpebral"
    if "forniceal" in name:
        return "forniceal"
    if image_path.suffix.lower() in {".jpg", ".jpeg"}:
        return "original_jpg"

    return "other"


def detect_folder_classes(image_files):
    class_counts = {}

    for image_path in image_files:
        parts = [part.lower() for part in image_path.parts]

        if "anemic" in parts:
            label = "Anemic"
        elif "non-anemic" in parts or "non_anemic" in parts:
            label = "Non-anemic"
        else:
            label = "Unknown"

        class_counts[label] = class_counts.get(label, 0) + 1

    return class_counts


def audit_images(image_files, sample_count):
    print("\n" + "=" * 70)
    print("IMAGE AUDIT")
    print("=" * 70)

    print(f"Total image count: {len(image_files)}")

    if not image_files:
        print("No images found.")
        return

    print("\nFolder-based class counts:")
    class_counts = detect_folder_classes(image_files)
    for label, count in class_counts.items():
        print(f"- {label}: {count}")

    print("\nImage type counts:")
    image_type_counts = {}
    for image_path in image_files:
        image_type = classify_image_type(image_path)
        image_type_counts[image_type] = image_type_counts.get(image_type, 0) + 1

    for image_type, count in image_type_counts.items():
        print(f"- {image_type}: {count}")

    print("\nSample image paths:")
    for image_path in image_files[:sample_count]:
        print(f"- {image_path}")

    print("\nSample image sizes:")
    for image_path in image_files[:sample_count]:
        image = cv2.imread(str(image_path))

        if image is None:
            print(f"- {image_path.name}: Could not read image")
            continue

        height, width, channels = image.shape
        image_type = classify_image_type(image_path)

        print(
            f"- {image_path.name}: "
            f"type={image_type}, width={width}, height={height}, channels={channels}"
        )


def read_table(table_path):
    suffix = table_path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(table_path)

    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(table_path)

    raise ValueError(f"Unsupported table file: {table_path}")


def audit_tables(table_files, sample_count):
    print("\n" + "=" * 70)
    print("CSV / EXCEL AUDIT")
    print("=" * 70)

    print(f"CSV/Excel file count: {len(table_files)}")

    if not table_files:
        print("No CSV or Excel files found.")
        return

    for table_path in table_files:
        print("\n" + "-" * 70)
        print(f"Table file: {table_path}")
        print("-" * 70)

        try:
            df = read_table(table_path)
        except Exception as error:
            print(f"Could not read table: {table_path}")
            print(f"Error: {error}")
            continue

        print("\nDataset shape:")
        print(f"Rows: {df.shape[0]}")
        print(f"Columns: {df.shape[1]}")

        print("\nColumns:")
        for column in df.columns:
            print(f"- {column}")

        print(f"\nFirst {sample_count} rows:")
        print(df.head(sample_count))

        print("\nMissing values:")
        print(df.isnull().sum())

        print("\nColumn data types:")
        print(df.dtypes)

        print("\nPossible Hb/anemia related columns:")
        found_related_column = False

        for column in df.columns:
            col_lower = str(column).lower()

            if (
                "hb" in col_lower
                or "hemoglobin" in col_lower
                or "haemoglobin" in col_lower
                or "anemia" in col_lower
                or "anaemia" in col_lower
                or "label" in col_lower
                or "class" in col_lower
                or "diagnosis" in col_lower
            ):
                print(f"- {column}")
                found_related_column = True

        if not found_related_column:
            print("- No obvious Hb/anemia column found")


def main():
    parser = argparse.ArgumentParser(description="Arova dataset audit script")

    parser.add_argument(
        "--data_dir",
        type=str,
        required=True,
        help="Dataset folder path, example: data/raw/dataset_1"
    )

    parser.add_argument(
        "--sample_count",
        type=int,
        default=5,
        help="Number of sample images/table rows to print"
    )

    args = parser.parse_args()

    dataset_path = Path(args.data_dir)

    print("\n" + "#" * 70)
    print("AROVA DATASET AUDIT")
    print("#" * 70)

    print(f"\nDataset folder: {dataset_path.resolve()}")

    if not dataset_path.exists():
        print("\nERROR: Dataset folder does not exist.")
        return

    image_files = find_files(dataset_path, IMAGE_EXTENSIONS)
    table_files = find_files(dataset_path, TABLE_EXTENSIONS)

    audit_images(image_files, args.sample_count)
    audit_tables(table_files, args.sample_count)

    print("\n" + "#" * 70)
    print("AUDIT COMPLETE")
    print("#" * 70)

    print("\nSafety note:")
    print(
        "This is a preliminary screening result, not a final diagnosis. "
        "Please confirm with a clinical hemoglobin blood test."
    )


if __name__ == "__main__":
    main()