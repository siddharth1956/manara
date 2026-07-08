import streamlit as st
import requests

API = "http://127.0.0.1:8000/query"


def show_ai_chat():

    st.title("🤖 MANARA AI Assistant")
    st.caption(
        "Powered by Retrieval-Augmented Generation (RAG), Sentinel-2, OpenStreetMap, FAISS and Llama 3.2"
    )

    st.divider()

    # -----------------------------
    # Session State
    # -----------------------------
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # -----------------------------
    # Welcome Screen
    # -----------------------------
    if len(st.session_state.messages) == 0:

        st.info(
            """
### 👋 Welcome to MANARA

You can ask questions like:

• Which Sentinel image has the lowest cloud cover?

• Show recent Sentinel-2A acquisitions.

• Analyze vegetation.

• Find road information.

• Which satellite captured this scene?

• Show images with cloud cover below 10%.
"""
        )

    # -----------------------------
    # Display Chat History
    # -----------------------------
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            if message["role"] == "assistant":

                if "confidence" in message:

                    c1, c2, c3 = st.columns(3)

                    c1.metric(
                        "Confidence",
                        f"{message['confidence']}%"
                    )

                    c2.metric(
                        "Sources",
                        message["num_sources"]
                    )

                    c3.metric(
                        "Model",
                        "Llama 3.2"
                    )

                if "sources" in message:

                    with st.expander("📚 Retrieved Sources"):

                        for i, src in enumerate(message["sources"]):

                            st.markdown(f"### Source {i+1}")

                            st.write(src["text"])

                            st.caption(
                                f"Similarity Distance : {src['distance']:.4f}"
                            )

                            st.divider()

    # -----------------------------
    # Chat Input
    # -----------------------------
    prompt = st.chat_input("Ask MANARA...")

    if prompt:

        user_message = {
            "role": "user",
            "content": prompt
        }

        st.session_state.messages.append(user_message)

        with st.chat_message("user"):

            st.markdown(prompt)

        with st.chat_message("assistant"):

            with st.spinner("🛰️ Searching satellite database..."):

                try:

                    response = requests.post(
                        API,
                        json={
                            "question": prompt
                        },
                        timeout=120
                    )

                    data = response.json()

                    answer = data["answer"]

                    sources = data.get("sources", [])

                    if len(sources) > 0:

                        best_distance = sources[0]["distance"]

                        confidence = max(
                            0,
                            round(100 - best_distance * 2, 1)
                        )

                    else:

                        confidence = 0

                    st.success("Analysis Complete")

                    st.markdown(answer)

                    st.divider()

                    c1, c2, c3 = st.columns(3)

                    c1.metric(
                        "Confidence",
                        f"{confidence}%"
                    )

                    c2.metric(
                        "Retrieved Sources",
                        len(sources)
                    )

                    c3.metric(
                        "Model",
                        "Llama 3.2"
                    )

                    if len(sources) > 0:

                        with st.expander(
                            "📚 Retrieved Sources",
                            expanded=False
                        ):

                            for i, src in enumerate(sources):

                                st.markdown(f"### Source {i+1}")

                                st.write(src["text"])

                                st.caption(
                                    f"Similarity Distance : {src['distance']:.4f}"
                                )

                                st.divider()

                    assistant_message = {

                        "role": "assistant",

                        "content": answer,

                        "sources": sources,

                        "confidence": confidence,

                        "num_sources": len(sources)

                    }

                    st.session_state.messages.append(
                        assistant_message
                    )

                except Exception as e:

                    st.error(f"Connection Error\n\n{e}")

    # -----------------------------
    # Sidebar Controls
    # -----------------------------
    st.sidebar.divider()

    st.sidebar.subheader("💬 Chat Controls")

    if st.sidebar.button(
        "🗑 Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()

    st.sidebar.divider()

    st.sidebar.subheader("💡 Example Questions")

    st.sidebar.markdown("""
- Which Sentinel image has the lowest cloud cover?

- Analyze vegetation.

- Show recent Sentinel images.

- Find roads near Dubai.

- Which satellite captured this image?

- Show Sentinel-2A scenes.

- Compare cloud cover.
""")