import streamlit as st
from pathlib import Path

from views.dashboard import show_dashboard
from views.ai_chat import show_ai_chat
from views.analytics import show_analytics
from views.maps import show_maps
from views.satellite import show_satellite
from views.roads import show_roads
from views.datasets import show_datasets
from views.settings import show_settings

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="MANARA AI",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Load Custom CSS
# -----------------------------
css_file = Path(__file__).parent / "assets" / "styles.css"

if css_file.exists():
    with open(css_file) as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

# -----------------------------
# Session State
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("🛰️ MANARA AI")
st.sidebar.caption("Geospatial Intelligence Platform")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "AI Chat",
        "Satellite Explorer",
        "Road Network",
        "Analytics",
        "Interactive Map",
        "Dataset Explorer",
        "Settings",
    ]
)

# -----------------------------
# Footer in Sidebar
# -----------------------------
st.sidebar.markdown("---")
st.sidebar.success("Backend Online")
st.sidebar.success("FAISS Loaded")
st.sidebar.success("Ollama Connected")
st.sidebar.success("Copernicus Connected")

st.sidebar.markdown("---")
st.sidebar.caption("Version 1.0")
st.sidebar.caption("University of Birmingham Dubai")

# -----------------------------
# Routing
# -----------------------------
if page == "Dashboard":
    show_dashboard()

elif page == "AI Chat":
    show_ai_chat()

elif page == "Satellite Explorer":
    show_satellite()

elif page == "Road Network":
    show_roads()

elif page == "Analytics":
    show_analytics()

elif page == "Interactive Map":
    show_maps()

elif page == "Dataset Explorer":
    show_datasets()

elif page == "Settings":
    show_settings()