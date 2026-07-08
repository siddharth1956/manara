import json
from pathlib import Path

from app.services.copernicus_service import search_sentinel_products

results = search_sentinel_products(top=20)

output_dir = Path("data/raw/copernicus")
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "sentinel_products.json"

with open(output_file, "w") as f:
    json.dump(results, f, indent=2)

print(f"Saved metadata to: {output_file}")
print(f"Products returned: {len(results['value'])}")