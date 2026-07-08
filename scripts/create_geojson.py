import pandas as pd
import geopandas as gpd
import numpy as np
from shapely import wkt

df = pd.read_csv(
    "data/processed/dubai_roads.csv"
)

# Convert WKT text to geometry
df["geometry"] = df["geometry"].apply(wkt.loads)

# Clean highway column BEFORE exporting
def clean(value):

    if isinstance(value, str):

        value = value.replace("[", "")
        value = value.replace("]", "")
        value = value.replace("'", "")

        if "," in value:
            value = value.split(",")[0]

        return value.strip()

    return value

df["highway"] = df["highway"].apply(clean)

gdf = gpd.GeoDataFrame(
    df,
    geometry="geometry",
    crs="EPSG:4326"
)

gdf.to_file(
    "data/processed/dubai_roads.geojson",
    driver="GeoJSON"
)

print("✅ GeoJSON recreated successfully.")