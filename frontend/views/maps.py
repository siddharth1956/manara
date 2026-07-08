import ast

import streamlit as st
import folium

from folium.plugins import Fullscreen, MarkerCluster
from streamlit_folium import st_folium

from utils.interactive_map import load_map


def show_maps():

    st.title("🗺 Interactive Map")

    st.caption(
        "Explore Sentinel imagery across the UAE."
    )

    st.divider()

    df = load_map()

    # ---------------------------------
    # Filters
    # ---------------------------------

    col1, col2 = st.columns(2)

    with col1:

        search = st.text_input(
            "Search Image ID"
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
        "Maximum Cloud Cover (%)",
        0,
        100,
        100
    )

    # ---------------------------------
    # Apply Filters
    # ---------------------------------

    if search:

        df = df[
            df["id"].str.contains(
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
        f"{len(df)} image(s) displayed."
    )

    # ---------------------------------
    # Map
    # ---------------------------------

    m = folium.Map(
        location=[24.4, 54.4],
        zoom_start=7,
        tiles="CartoDB dark_matter"
    )

    Fullscreen().add_to(m)

    marker_cluster = MarkerCluster().add_to(m)

    # ---------------------------------
    # Add Markers
    # ---------------------------------

    for _, row in df.iterrows():

        try:

            bbox = ast.literal_eval(row["bbox"])

            lon = float(bbox[0])
            lat = float(bbox[1])

        except Exception:

            continue

        cloud_cover = float(row["cloud_cover"])

        if cloud_cover < 20:
            color = "green"

        elif cloud_cover < 50:
            color = "orange"

        else:
            color = "red"

        popup = f"""
        <b>{row['id']}</b><br><br>

        <b>Platform:</b> {row['platform']}<br>
        <b>Constellation:</b> {row['constellation']}<br>
        <b>Cloud Cover:</b> {cloud_cover}%<br>
        <b>Date:</b> {row['datetime']}
        """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(
                popup,
                max_width=350
            ),
            tooltip=row["id"],
            icon=folium.Icon(
                color=color,
                icon="cloud"
            )
        ).add_to(marker_cluster)

    folium.LayerControl().add_to(m)

    st_folium(
        m,
        height=700,
        use_container_width=True
    )