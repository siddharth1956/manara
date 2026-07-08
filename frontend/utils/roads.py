import pandas as pd


def load_roads():

    return pd.read_csv(
        "data/processed/dubai_roads.csv"
    )


def total_roads():

    return len(load_roads())


def total_length():

    df = load_roads()

    return round(df["length"].sum(), 2)


def road_types():

    df = load_roads()

    return df["highway"].astype(str).nunique()


def df_highways():

    return load_roads()


def highway_distribution():

    df = load_roads()

    # Remove missing values
    df = df.dropna(subset=["highway"])

    # Convert to string
    df["highway"] = df["highway"].astype(str)

    # Remove brackets and quotes
    df["highway"] = (
        df["highway"]
            .str.replace("[", "", regex=False)
            .str.replace("]", "", regex=False)
            .str.replace("'", "", regex=False)
    )

    # If multiple road types exist, keep only the first one
    df["highway"] = df["highway"].str.split(",").str[0].str.strip()

    # Count road types
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