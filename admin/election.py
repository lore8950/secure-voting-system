import streamlit as st

from database import (
    get_election_settings,
    set_election_end_time,
    toggle_election
)


def election_page():

    st.title("⏱ Election Management")

    row = get_election_settings()

    active = bool(row[1])

    st.subheader("Election Timer")

    col1, col2 = st.columns(2)

    with col1:

        hours = st.number_input(
            "Duration (Hours)",
            min_value=0.5,
            max_value=72.0,
            value=1.0
        )

        if st.button("🕐 Set Timer"):

            set_election_end_time(hours)

            st.success("✅ Election timer updated.")

            st.rerun()

    with col2:

        if active:

            st.success("🟢 Election is Running")

            if st.button("🔴 Stop Election"):

                toggle_election(False)

                st.success("Election Stopped")

                st.rerun()

        else:

            st.error("🔴 Election is Closed")

            if st.button("🟢 Start Election"):

                toggle_election(True)

                st.success("Election Started")

                st.rerun()