import pandas as pd

from app.core.config import PROCESSED_DATA_DIR


df = pd.read_csv(
    PROCESSED_DATA_DIR / "stac_metadata.csv"
)


def total_images():

    return len(df)


def average_cloud_cover():

    return round(
        df["cloud_cover"].mean(),
        2
    )


def minimum_cloud_cover():

    row = df.loc[
        df["cloud_cover"].idxmin()
    ]

    return {

        "image": row["id"],

        "cloud_cover": row["cloud_cover"]

    }


def maximum_cloud_cover():

    row = df.loc[
        df["cloud_cover"].idxmax()
    ]

    return {

        "image": row["id"],

        "cloud_cover": row["cloud_cover"]

    }


def platform_counts():

    return (
        df["platform"]
        .value_counts()
        .to_dict()
    )