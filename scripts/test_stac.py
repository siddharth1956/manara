import json

from app.services.stac_service import search_uae_sentinel

print("=" * 60)
print("Searching UAE Sentinel-2 Products")
print("=" * 60)

results = search_uae_sentinel()

print(f"Products Found: {len(results.get('features', []))}")

with open("data/raw/copernicus/stac_results.json", "w") as f:
    json.dump(results, f, indent=2)
