import json
import pandas as pd
from pathlib import Path

input_file = Path("data/raw/copernicus/sentinel_products.json")

with open(input_file, "r") as f:
    data = json.load(f)

rows = []

for product in data["value"]:
    rows.append({
        "id": product["Id"],
        "name": product["Name"],
        "date": product["ContentDate"]["Start"],
        "size_mb": round(product["ContentLength"] / (1024 * 1024), 2),
        "online": product["Online"],
    })

df = pd.DataFrame(rows)

output_file = Path("data/processed/sentinel_metadata.csv")
df.to_csv(output_file, index=False)

print(df.head())
print(f"\nSaved to: {output_file}")