import pandas as pd


def load_satellite():

    return pd.read_csv(
        "data/processed/stac_metadata.csv"
    )


def load_roads():

    return pd.read_csv(
        "data/processed/dubai_roads.csv"
    )


def total_images():

    return len(load_satellite())


def total_roads():

    return len(load_roads())


def average_cloud():

    df = load_satellite()

    return round(
        df["cloud_cover"].mean(),
        2
    )