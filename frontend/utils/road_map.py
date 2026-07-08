import json


def load_road_map():

    with open(
        "data/processed/dubai_roads.geojson",
        "r",
        encoding="utf-8"
    ) as f:

        geojson = json.load(f)

    return geojson
