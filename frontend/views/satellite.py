import streamlit as st
from utils.satellite import *
from components.satellite_card import satellite_card


def show_satellite():

    st.title("🛰 Satellite Explorer")

    st.caption(
        "Browse and filter Sentinel imagery stored inside MANARA."
    )

    st.divider()

    # ----------------------------
    # Statistics
    # ----------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Images",
        total_images()
    )

    c2.metric(
        "Average Cloud",
        f"{average_cloud()}%"
    )

    c3.metric(
        "Lowest Cloud",
        f"{minimum_cloud()}%"
    )

    c4.metric(
        "Highest Cloud",
        f"{maximum_cloud()}%"
    )

    st.divider()

    # ----------------------------
    # Load Dataset
    # ----------------------------

    df = load_satellite()

    # ----------------------------
    # Filters
    # ----------------------------

    st.subheader("🔍 Search & Filters")

    col1, col2 = st.columns(2)

    with col1:

        search = st.text_input(
            "Search Image ID",
            placeholder="Example: S2A_MSIL2A..."
        )

    with col2:

        satellite = st.selectbox(
            "Satellite",
            [
                "All",
                "sentinel-2a",
                "sentinel-2b"
            ]
        )

    col3, col4 = st.columns(2)

    with col3:

        cloud = st.slider(
            "Maximum Cloud Cover (%)",
            0,
            100,
            100
        )

    with col4:

        sort = st.selectbox(
            "Sort By",
            [
                "Newest",
                "Oldest",
                "Lowest Cloud",
                "Highest Cloud"
            ]
        )

    # ----------------------------
    # Apply Search
    # ----------------------------

    if search:

        df = df[
            df["id"].str.contains(
                search,
                case=False,
                na=False
            )
        ]

    # ----------------------------
    # Apply Satellite Filter
    # ----------------------------

    if satellite != "All":

        df = df[
            df["platform"] == satellite
        ]

    # ----------------------------
    # Apply Cloud Filter
    # ----------------------------

    df = df[
        df["cloud_cover"] <= cloud
    ]

    # ----------------------------
    # Sorting
    # ----------------------------

    if sort == "Newest":

        df = df.sort_values(
            "datetime",
            ascending=False
        )

    elif sort == "Oldest":

        df = df.sort_values(
            "datetime",
            ascending=True
        )

    elif sort == "Lowest Cloud":

        df = df.sort_values(
            "cloud_cover",
            ascending=True
        )

    elif sort == "Highest Cloud":

        df = df.sort_values(
            "cloud_cover",
            ascending=False
        )

    # ----------------------------
    # Results
    # ----------------------------

    st.divider()

    st.success(
        f"Found {len(df)} satellite image(s)."
    )

    st.divider()

    st.subheader("🛰 Available Satellite Images")

    for _, row in df.iterrows():

        satellite_card(row)

        st.markdown("")