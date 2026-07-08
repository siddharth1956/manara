import streamlit as st


def cloud_color(cloud):

    if cloud <= 10:
        return "🟢"

    elif cloud <= 30:
        return "🟡"

    return "🔴"


def satellite_card(row):

    tile = row["id"].split("_")[5]

    with st.container(border=True):

        st.subheader("🛰 " + row["platform"].upper())

        c1, c2 = st.columns(2)

        with c1:

            st.write("**📅 Date**")
            st.write(row["datetime"][:10])

            st.write("**🗺 Tile**")
            st.write(tile)

        with c2:

            st.write("**☁ Cloud Cover**")
            st.write(
                f"{cloud_color(row['cloud_cover'])} {row['cloud_cover']}%"
            )

            st.write("**🌍 Constellation**")
            st.write(row["constellation"])

        b1, b2 = st.columns(2)

        with b1:

            st.button(
                "👁 View Details",
                key=f"view_{row['id']}"
            )

        with b2:

            st.button(
                "🤖 Analyze",
                key=f"ai_{row['id']}"
            )