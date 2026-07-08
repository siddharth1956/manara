import pandas as pd

from utils.satellite import load_satellite


def load_map_data():
    df = load_satellite()

    df["lat"] = df["bbox"].apply(
        lambda x: eval(x)[1]
    )

    df["lon"] = df["bbox"].apply(
        lambda x: eval(x)[0]
    )

    return df