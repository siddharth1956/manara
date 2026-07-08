import streamlit as st

from utils.datasets import load_dataset


def show_datasets():

    st.title("🗂 Dataset Explorer")

    st.caption(
        "Browse every satellite dataset available inside MANARA."
    )

    st.divider()

    df = load_dataset()

    col1, col2 = st.columns(2)

    with col1:

        search = st.text_input(
            "Search Dataset ID"
        )

    with col2:

        platform = st.selectbox(
            "Platform",
            [
                "All",
                "sentinel-2a",
                "sentinel-2b"
            ]
        )

    cloud = st.slider(
        "Maximum Cloud Cover",
        0,
        100,
        100
    )

    if search:

        df = df[
            df["id"]
            .str.contains(
                search,
                case=False,
                na=False
            )
        ]

    if platform != "All":

        df = df[
            df["platform"] == platform
        ]

    df = df[
        df["cloud_cover"] <= cloud
    ]

    st.success(
        f"{len(df)} dataset(s) found."
    )

    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True
    )

    st.download_button(
        "⬇ Download CSV",
        df.to_csv(index=False),
        "filtered_dataset.csv",
        "text/csv"
    )