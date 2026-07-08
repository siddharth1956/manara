from pathlib import Path
import pandas as pd

# Get project root
BASE_DIR = Path(__file__).resolve().parent.parent

# CSV path
csv_path = BASE_DIR / "data" / "raw" / "uae_metadata.csv"

# Read CSV
df = pd.read_csv(csv_path)

print("\n===== UAE Metadata =====\n")
print(df)

print("\nDataset Information\n")
print(df.info())