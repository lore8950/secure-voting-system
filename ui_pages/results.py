import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

def results_page():

    st.header("📊 Election Results")

    conn = sqlite3.connect("secure_voting.db")
    c = conn.cursor()

    c.execute("""
        SELECT name, party, votes_count
        FROM candidates
        ORDER BY votes_count DESC
    """)

    results = c.fetchall()

    conn.close()

    if results:

        df = pd.DataFrame(
            results,
            columns=["Candidate", "Party", "Votes"]
        )

        total = df["Votes"].sum()

        fig_pie = px.pie(
            df,
            values="Votes",
            names="Candidate",
            hole=0.4,
            template="plotly_dark"
        )

        st.plotly_chart(
            fig_pie,
            use_container_width=True
        )

        fig_bar = px.bar(
            df,
            x="Candidate",
            y="Votes",
            color="Party",
            text="Votes",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True
        )

        st.subheader("🏆 Leaderboard")

        for i, (name, party, votes) in enumerate(results):

            medal = ["🥇","🥈","🥉"][i] if i < 3 else "🔹"

            pct = round(
                votes / total * 100,
                1
            ) if total > 0 else 0

            st.markdown(
                f"""
                <div class='voter-card'>
                {medal} <b>{name}</b><br>
                {party}<br>
                Votes : {votes}<br>
                {pct}%
                </div>
                """,
                unsafe_allow_html=True
            )