import pandas as pd

DATA = "data/processed/stac_metadata.csv"


def load_satellite():

    return pd.read_csv(DATA)


def total_images():

    return len(load_satellite())


def average_cloud():

    df = load_satellite()

    return round(df["cloud_cover"].mean(), 2)


def minimum_cloud():

    df = load_satellite()

    return round(df["cloud_cover"].min(), 2)


def maximum_cloud():

    df = load_satellite()

    return round(df["cloud_cover"].max(), 2)