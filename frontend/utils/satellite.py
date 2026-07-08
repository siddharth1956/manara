from pathlib import Path
import pandas as pd

DATA = Path("data/processed/stac_metadata.csv")


def load_satellite():

    if not DATA.exists():
        return pd.DataFrame(
            columns=["cloud_cover"]
        )

    return pd.read_csv(DATA)


def total_images():

    return len(load_satellite())


def average_cloud():

    df = load_satellite()

    if df.empty:
        return 0

    return round(df["cloud_cover"].mean(), 2)


def minimum_cloud():

    df = load_satellite()

    if df.empty:
        return 0

    return round(df["cloud_cover"].min(), 2)


def maximum_cloud():

    df = load_satellite()

    if df.empty:
        return 0

    return round(df["cloud_cover"].max(), 2)
