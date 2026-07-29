from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT_DIR / "data" / "labels" / "binary" / "dataset_2_binary_labels.csv"

df = pd.read_csv(CSV_PATH)

print("\nTotal rows:")
print(len(df))

print("\nClass balance:")
print(df["label"].value_counts())

print("\nSample image paths:")
for path in df["image_path"].head(30):
    print(path)

print("\nPossible image type keyword counts:")
keywords = [
    "original",
    "forniceal",
    "palpebral",
    "forniceal_palpebral",
    "seg",
    "segment",
    "mask"
]

for keyword in keywords:
    count = df["image_path"].astype(str).str.lower().str.contains(keyword).sum()
    print(f"{keyword}: {count}")