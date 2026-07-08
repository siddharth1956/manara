import geopandas as gpd
import numpy as np


def load_road_map():

    gdf = gpd.read_file(
        "data/processed/dubai_roads.geojson"
    )

    # Convert ndarray values to strings
    def clean(value):

        if isinstance(value, np.ndarray):

            if len(value) == 0:
                return ""

            return str(value[0])

        return value

    for col in gdf.columns:

        if col != "geometry":

            gdf[col] = gdf[col].apply(clean)

    return gdf