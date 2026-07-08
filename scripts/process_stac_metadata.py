import json
import pandas as pd
from pathlib import Path

input_file = Path("data/raw/copernicus/stac_results.json")

with open(input_file, "r") as f:
    data = json.load(f)

rows = []

for feature in data["features"]:

    props = feature["properties"]

    rows.append({
        "id": feature["id"],
        "datetime": props.get("datetime"),
        "cloud_cover": props.get("eo:cloud_cover"),
        "platform": props.get("platform"),
        "constellation": props.get("constellation"),
        "bbox": str(feature.get("bbox")),
    })

df = pd.DataFrame(rows)

output = Path("data/processed/stac_metadata.csv")
df.to_csv(output, index=False)

print(df.head())

print("\nSaved to:", output)