import streamlit as st
import plotly.express as px

from utils.satellite import *
from utils.roads import *


def show_dashboard():

    # =====================================================
    # Header
    # =====================================================

    st.title("🛰 MANARA AI")

    st.subheader(
        "Geospatial Intelligence Platform"
    )

    st.caption(
        "Real-time satellite intelligence powered by Copernicus, OpenStreetMap, FAISS and Ollama."
    )

    st.divider()

    # =====================================================
    # KPI Cards
    # =====================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "🛰 Satellite Images",
            total_images(),
            "Latest Sentinel-2"
        )

    with col2:

        st.metric(
            "☁ Average Cloud",
            f"{average_cloud()}%",
            "Across all scenes"
        )

    with col3:

        st.metric(
            "🛣 Road Segments",
            f"{total_roads():,}",
            "OpenStreetMap"
        )

    with col4:

        st.metric(
            "🤖 AI Assistant",
            "ONLINE",
            "Ollama + FAISS"
        )

    st.divider()

    # =====================================================
    # Load Dataset
    # =====================================================

    df = load_satellite()

    # =====================================================
    # Charts
    # =====================================================

    left, right = st.columns(2)

    # ------------------------------------------
    # Cloud Cover Distribution
    # ------------------------------------------

    with left:

        st.subheader("☁ Cloud Cover Distribution")

        fig = px.histogram(
            df,
            x="cloud_cover",
            nbins=10,
            title="Cloud Cover Distribution"
        )

        fig.update_layout(
            template="plotly_dark",
            height=420,
            showlegend=False,
            margin=dict(
                l=20,
                r=20,
                t=40,
                b=20
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ------------------------------------------
    # Platform Distribution
    # ------------------------------------------

    with right:

        st.subheader("🛰 Platform Distribution")

        platform = (
            df["platform"]
            .value_counts()
            .reset_index()
        )

        platform.columns = [
            "Platform",
            "Images"
        ]

        fig = px.pie(
            platform,
            names="Platform",
            values="Images",
            hole=0.60
        )

        fig.update_layout(
            template="plotly_dark",
            height=420,
            margin=dict(
                l=20,
                r=20,
                t=40,
                b=20
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.divider()
    left, right = st.columns([2,1])
    with left:
         st.subheader("🛰 Recent Satellite Images")


   