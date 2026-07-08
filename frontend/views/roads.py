import streamlit as st
import plotly.express as px
import folium

from streamlit_folium import st_folium

from utils.roads import *
from utils.road_map import load_road_map


def show_roads():

    st.title("🛣 Road Network Explorer")

    st.caption(
        "Analyze and visualize the OpenStreetMap road network."
    )

    st.divider()

    # ==========================
    # Statistics
    # ==========================

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Road Segments",
        f"{total_roads():,}"
    )

    c2.metric(
        "Total Length (m)",
        f"{total_length():,.0f}"
    )

    c3.metric(
        "Road Types",
        road_types()
    )

    st.divider()

    # ==========================
    # Road Type Chart
    # ==========================

    st.subheader("📊 Road Type Distribution")

    chart = highway_distribution().head(10)

    fig = px.bar(
        chart,
        x="Road Type",
        y="Count",
        color="Count",
        text="Count",
        height=500
    )

    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_tickangle=-40
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    # ==========================
    # Interactive GIS Map
    # ==========================

    st.subheader("🗺 Interactive Road Map")

    gdf = load_road_map()

    m = folium.Map(
        location=[25.20,55.27],
        zoom_start=11,
        tiles="CartoDB dark_matter"
    )

    folium.GeoJson(
        gdf,
        style_function=lambda feature: {
            "color":"#00FFFF",
            "weight":2,
            "opacity":0.8
        },
        tooltip=folium.GeoJsonTooltip(
            fields=[
                "name",
                "highway",
                "length"
            ],
            aliases=[
                "Road",
                "Type",
                "Length (m)"
            ]
        )
    ).add_to(m)

    st_folium(
        m,
        height=700,
        use_container_width=True
    )

    st.divider()

    # ==========================
    # Search
    # ==========================

    st.subheader("🔍 Search Roads")

    df = load_roads()

    road = st.text_input(
        "Road Name"
    )

    if road:

        df = df[
            df["name"]
            .fillna("")
            .str.contains(
                road,
                case=False
            )
        ]

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )