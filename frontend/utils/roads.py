from pathlib import Path
import pandas as pd

DATA = Path("data/processed/dubai_roads.csv")


def load_roads():

    if not DATA.exists():

        return pd.DataFrame(
            columns=[
                "length",
                "highway"
            ]
        )

    return pd.read_csv(DATA)


def total_roads():

    return len(load_roads())


def total_length():

    df = load_roads()

    if df.empty:
        return 0

    return round(df["length"].sum(), 2)


def road_types():

    df = load_roads()

    if df.empty:
        return 0

    return df["highway"].astype(str).nunique()


def df_highways():

    return load_roads()


def highway_distribution():

    df = load_roads()

    if df.empty:

        return pd.DataFrame(
            columns=[
                "Road Type",
                "Count"
            ]
        )

    df = df.dropna(subset=["highway"])

    df["highway"] = df["highway"].astype(str)

    df["highway"] = (
        df["highway"]
        .str.replace("[", "", regex=False)
        .str.replace("]", "", regex=False)
        .str.replace("'", "", regex=False)
    )

    df["highway"] = (
        df["highway"]
        .str.split(",")
        .str[0]
        .str.strip()
    )

    chart = (
        df["highway"]
        .value_counts()
        .reset_index()
    )

    chart.columns = [
        "Road Type",
        "Count"
    ]

    return chart
