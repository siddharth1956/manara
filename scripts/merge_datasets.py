import pandas as pd

# Load datasets
stac = pd.read_csv("data/processed/stac_metadata.csv")
roads = pd.read_csv("data/processed/dubai_roads.csv")

print("=" * 60)
print("MANARA DATA MERGER")
print("=" * 60)

print("Satellite Images:", len(stac))
print("Road Segments:", len(roads))

# Cross join (prototype)
merged = stac.merge(
    roads,
    how="cross"
)

print("\nMerged Dataset Shape:")
print(merged.shape)

merged.to_csv(
    "data/processed/manara_dataset.csv",
    index=False
)

print("\nSaved to:")
print("data/processed/manara_dataset.csv")