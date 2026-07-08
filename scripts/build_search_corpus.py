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
# Add Road Network Document
# -------------------------------------------------------

road_document = {

    "id": "dubai_roads",

    "type": "roads",

    "platform": "OpenStreetMap",

    "constellation": "",

    "datetime": "",

    "cloud_cover": "",

    "bbox": "",

    "text": """
Dubai Road Network

Source:
OpenStreetMap

Total Road Segments:
125099

Applications:

- Route Planning
- Traffic Analysis
- Navigation
- Smart City Planning
- GIS Analysis
- Infrastructure Monitoring
- Geospatial Intelligence
"""
}

documents.append(road_document)

corpus = pd.DataFrame(documents)

output = Path("data/processed/search_corpus.csv")

corpus.to_csv(output, index=False)

print("\nCorpus Created Successfully!")

print(corpus.head())

print("\nTotal Documents:", len(corpus))

print("\nSaved to:", output)