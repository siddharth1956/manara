import streamlit as st
import plotly.express as px

from utils.analytics import *


def show_analytics():

    st.title("📊 Analytics Dashboard")

    st.caption(
        "Analyze satellite imagery statistics and remote sensing indicators."
    )

    st.divider()

    # ---------------------------------
    # KPI Metrics
    # ---------------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Satellite Images",
        total_images()
    )

    c2.metric(
        "Average Cloud",
        f"{average_cloud()}%"
    )

    c3.metric(
        "Lowest Cloud",
        f"{lowest_cloud()}%"
    )

    c4.metric(
        "Highest Cloud",
        f"{highest_cloud()}%"
    )

    st.divider()

    # ---------------------------------
    # Charts
    # ---------------------------------

    left, right = st.columns(2)

    with left:

        st.subheader("☁ Cloud Cover Distribution")

        fig = px.histogram(
            cloud_distribution(),
            x="cloud_cover",
            nbins=10,
            marginal="box",
            title="Cloud Cover (%)"
        )

        fig.update_layout(
            showlegend=False,
            xaxis_title="Cloud Cover (%)",
            yaxis_title="Number of Images",
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:

        st.subheader("🛰 Platform Distribution")

        fig = px.pie(
            platform_distribution(),
            names="Platform",
            values="Count",
            hole=0.55
        )

        fig.update_layout(
            height=450
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.divider()

    # ---------------------------------
    # Images Per Day
    # ---------------------------------

    st.subheader("📅 Images Captured Per Day")

    fig = px.line(
        images_per_day(),
        x="date",
        y="Images",
        markers=True
    )

    fig.update_layout(
        xaxis_title="Capture Date",
        yaxis_title="Images",
        height=450
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    # ---------------------------------
    # Best Images
    # ---------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🌤 Lowest Cloud Images")

        st.dataframe(
            lowest_cloud_images(),
            hide_index=True,
            use_container_width=True
        )

    with col2:

        st.subheader("☁ Highest Cloud Images")

        st.dataframe(
            highest_cloud_images(),
            hide_index=True,
            use_container_width=True
        )

    st.divider()

    # ---------------------------------
    # Complete Dataset
    # ---------------------------------

    st.subheader("📄 Complete Dataset")

    st.dataframe(
        load_data(),
        hide_index=True,
        use_container_width=True
    )