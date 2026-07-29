from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]

excel_files = [
    ROOT_DIR / "data" / "raw" / "dataset_2" / "DS-anemia" / "India" / "India.xlsx",
    ROOT_DIR / "data" / "raw" / "dataset_2" / "DS-anemia" / "Italy" / "Italy.xlsx",
]

for excel_path in excel_files:
    print("\n" + "=" * 80)
    print(f"FILE: {excel_path}")
    print("=" * 80)

    df = pd.read_excel(excel_path)

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    for col in df.columns:
        print("-", col)

    print("\nFirst 5 rows:")
    print(df.head())