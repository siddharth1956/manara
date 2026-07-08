import streamlit as st


def show_settings():

    st.title("⚙ Settings")

    st.caption(
        "Configure MANARA AI preferences."
    )

    st.divider()

    st.subheader("🧠 AI Configuration")

    model = st.selectbox(
        "LLM Model",
        [
            "llama3.2",
            "mistral",
            "phi3"
        ]
    )

    temperature = st.slider(
        "Temperature",
        0.0,
        1.0,
        0.2
    )

    max_tokens = st.slider(
        "Maximum Tokens",
        256,
        4096,
        2048
    )

    st.divider()

    st.subheader("🛰 Satellite Settings")

    platform = st.selectbox(
        "Default Platform",
        [
            "Sentinel-2A",
            "Sentinel-2B"
        ]
    )

    cloud = st.slider(
        "Default Maximum Cloud (%)",
        0,
        100,
        30
    )

    st.divider()

    st.subheader("🎨 Appearance")

    theme = st.radio(
        "Theme",
        [
            "Dark",
            "Light"
        ]
    )

    st.toggle(
        "Enable Animations",
        value=True
    )

    st.toggle(
        "Show Tooltips",
        value=True
    )

    st.divider()

    if st.button(
        "💾 Save Settings",
        use_container_width=True
    ):
        st.success("Settings saved successfully.")