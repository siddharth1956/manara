import pandas as pd

DATA = "data/processed/stac_metadata.csv"


def load_dataset():

    return pd.read_csv(DATA)