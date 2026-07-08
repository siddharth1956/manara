import pandas as pd
from app.core.config import RAW_DATA_DIR, PROCESSED_DATA_DIR

# Load CSV
df = pd.read_csv(RAW_DATA_DIR / "uae_metadata.csv")

# Create a searchable text field
df["text"] = df.apply(
    lambda row: (
        f"Region: {row['region']}, "
        f"Date: {row['date']}, "
        f"NDVI: {row['ndvi']}, "
        f"Cloud Cover: {row['cloud_cover']}%, "
        f"Latitude: {row['latitude']}, "
        f"Longitude: {row['longitude']}"
    ),
    axis=1,
)

# Save processed dataset
output_path = PROCESSED_DATA_DIR / "uae_metadata_processed.csv"
df.to_csv(output_path, index=False)

print(df[["tile_id", "text"]])
print(f"\nSaved to: {output_path}")