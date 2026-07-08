import pandas as pd

# --------------------------------
# Dataset
# --------------------------------

DATA = "data/processed/stac_metadata.csv"


def load_data():

    return pd.read_csv(DATA)


# --------------------------------
# Basic Metrics
# --------------------------------

def total_images():

    return len(load_data())


def average_cloud():

    df = load_data()

    return round(
        df["cloud_cover"].mean(),
        2
    )


def lowest_cloud():

    df = load_data()

    return round(
        df["cloud_cover"].min(),
        2
    )


def highest_cloud():

    df = load_data()

    return round(
        df["cloud_cover"].max(),
        2
    )


# --------------------------------
# Platform Distribution
# --------------------------------

def platform_distribution():

    df = load_data()

    chart = (
        df["platform"]
        .fillna("Unknown")
        .value_counts()
        .reset_index()
    )

    chart.columns = [
        "Platform",
        "Count"
    ]

    return chart


# --------------------------------
# Cloud Distribution
# --------------------------------

def cloud_distribution():

    df = load_data()

    return df


# --------------------------------
# Images Per Date
# --------------------------------

def images_per_day():

    df = load_data()

    df["date"] = pd.to_datetime(df["datetime"]).dt.date

    chart = (
        df.groupby("date")
        .size()
        .reset_index(name="Images")
    )

    return chart


# --------------------------------
# Lowest Cloud Images
# --------------------------------

def lowest_cloud_images():

    df = load_data()

    return (
        df.sort_values(
            "cloud_cover"
        )
        .head(10)
    )


# --------------------------------
# Highest Cloud Images
# --------------------------------

def highest_cloud_images():

    df = load_data()

    return (
        df.sort_values(
            "cloud_cover",
            ascending=False
        )
        .head(10)
    )