import json
from pathlib import Path

from app.services.copernicus_service import search_uae_products

results = search_uae_products()

output_dir = Path("data/raw/copernicus")
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "uae_products.json"

with open(output_file, "w") as f:
    json.dump(results, f, indent=2)

print("Saved:", output_file)
print("Products:", len(results["value"]))