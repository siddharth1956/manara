import pandas as pd
from pathlib import Path

PROCESSED = Path("data/processed")
PROCESSED.mkdir(parents=True, exist_ok=True)

# -------------------------
# Demo STAC Metadata
# -------------------------

stac = pd.DataFrame({
    "id": [
        "S2A_001",
        "S2A_002",
        "S2B_003",
        "S2A_004",
        "S2B_005",
    ],
    "platform": [
        "Sentinel-2A",
        "Sentinel-2A",
        "Sentinel-2B",
        "Sentinel-2A",
        "Sentinel-2B",
    ],
    "cloud_cover": [
        2.5,
        8.1,
        15.3,
        4.7,
        21.9,
    ],
    "datetime": [
        "2026-06-01",
        "2026-06-05",
        "2026-06-10",
        "2026-06-15",
        "2026-06-20",
    ]
})

stac.to_csv(
    PROCESSED / "stac_metadata.csv",
    index=False
)

# -------------------------
# Demo Dubai Roads
# -------------------------

roads = pd.DataFrame({
    "name": [
        "Sheikh Zayed Road",
        "Al Khail Road",
        "Emirates Road",
        "Jumeirah Road",
        "Al Wasl Road",
    ],
    "highway": [
        "motorway",
        "trunk",
        "primary",
        "secondary",
        "secondary",
    ],
    "length": [
        55.2,
        41.7,
        70.8,
        18.4,
        22.6,
    ]
})

roads.to_csv(
    PROCESSED / "dubai_roads.csv",
    index=False
)

print("Demo datasets created successfully.")
