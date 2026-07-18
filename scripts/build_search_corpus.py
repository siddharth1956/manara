import json
import pandas as pd
from pathlib import Path

print("Loading STAC metadata...")

df = pd.read_csv("data/processed/stac_metadata.csv")

documents = []

for _, row in df.iterrows():

    document = f"""
Satellite Image Information

Image ID: {row['id']}

Capture Time:
{row['datetime']}

Platform:
{row['platform']}

Constellation:
{row['constellation']}

Cloud Cover:
{row['cloud_cover']} %

Bounding Box:
{row['bbox']}

Applications:
- Land cover monitoring
- Urban development
- Environmental monitoring
- Road extraction
- Change detection
- Infrastructure analysis
"""

    documents.append({

        "id": row["id"],

        "type": "satellite",

        "platform": row["platform"],

        "constellation": row["constellation"],

        "datetime": row["datetime"],

        "cloud_cover": row["cloud_cover"],

        "bbox": row["bbox"],

        "text": document

    })


# -------------------------------------------------------
# Road Documents (from the OSM Dubai roads dataset)
# -------------------------------------------------------
# Previously this was a single hardcoded document describing all
# 125,099 road segments as one blob, so every road query retrieved
# the same generic result regardless of which road or area was
# actually asked about. Instead, build one document per named road
# (a searchable "road entity") plus one document per highway type
# for segments that have no name in OSM, so none of the dataset is
# silently dropped.

print("Loading Dubai roads geojson...")

with open("data/processed/dubai_roads.geojson") as f:
    roads_geojson = json.load(f)


def extract_name(properties):

    name = properties.get("name")

    if isinstance(name, list):
        return name[0] if name else None

    return name


def compute_bbox(coordinate_lists):

    lons = []
    lats = []

    for coordinates in coordinate_lists:

        for lon, lat in coordinates:

            lons.append(lon)
            lats.append(lat)

    return [min(lons), min(lats), max(lons), max(lats)]


named_roads = {}
unnamed_by_type = {}

for feature in roads_geojson["features"]:

    properties = feature["properties"]
    geometry = feature["geometry"]

    name = extract_name(properties)
    highway = properties.get("highway") or "unclassified"
    length = properties.get("length") or 0
    coordinates = geometry.get("coordinates", [])

    if name:
        bucket = named_roads.setdefault(name, {
            "segments": 0,
            "length": 0.0,
            "highway_types": set(),
            "coordinates": []
        })
    else:
        bucket = unnamed_by_type.setdefault(highway, {
            "segments": 0,
            "length": 0.0,
            "highway_types": {highway},
            "coordinates": []
        })

    bucket["segments"] += 1
    bucket["length"] += length
    bucket["highway_types"].add(highway)
    bucket["coordinates"].append(coordinates)


def build_road_document(entity_id, label, stats):

    highway_types = ", ".join(sorted(stats["highway_types"]))
    total_km = round(stats["length"] / 1000, 2)
    bbox = compute_bbox(stats["coordinates"])

    text = f"""
Road Network Information

Road:
{label}

Road Type:
{highway_types}

Segments:
{stats['segments']}

Total Length:
{total_km} km

Source:
OpenStreetMap

Bounding Box:
{bbox}

Applications:
- Route Planning
- Traffic Analysis
- Navigation
- Smart City Planning
- GIS Analysis
- Infrastructure Monitoring
- Geospatial Intelligence
"""

    return {

        "id": entity_id,

        "type": "roads",

        "platform": "OpenStreetMap",

        "constellation": "",

        "datetime": "",

        "cloud_cover": "",

        "bbox": str(bbox),

        "text": text

    }


print(f"Building {len(named_roads)} named-road documents...")

for i, (name, stats) in enumerate(named_roads.items()):

    documents.append(
        build_road_document(f"road_named_{i}", name, stats)
    )

print(f"Building {len(unnamed_by_type)} unnamed-road-by-type documents...")

for highway, stats in unnamed_by_type.items():

    label = f"Unnamed {highway.replace('_', ' ')} roads in Dubai"

    documents.append(
        build_road_document(f"road_type_{highway}", label, stats)
    )


corpus = pd.DataFrame(documents)

output = Path("data/processed/search_corpus.csv")

corpus.to_csv(output, index=False)

print("\nCorpus Created Successfully!")

print(corpus.head())

print("\nTotal Documents:", len(corpus))

print("\nSaved to:", output)
