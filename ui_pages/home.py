import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

def home_page():

    conn = sqlite3.connect("secure_voting.db")
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM users WHERE role='Voter'")
    total_voters = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE has_voted=1")
    voted = c.fetchone()[0]

    c.execute("SELECT SUM(votes_count) FROM candidates")
    total_votes = c.fetchone()[0] or 0

    conn.close()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"<div class='metric-card'><h2>{total_voters}</h2><p>Total Voters</p></div>",
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"<div class='metric-card'><h2>{voted}</h2><p>Votes Cast</p></div>",
            unsafe_allow_html=True
        )

    with col3:
        pct = round((voted / total_voters * 100) if total_voters > 0 else 0, 1)
        st.markdown(
            f"<div class='metric-card'><h2>{pct}%</h2><p>Turnout</p></div>",
            unsafe_allow_html=True
        )

    st.markdown("### 🏆 Current Standing")

    conn = sqlite3.connect("secure_voting.db")
    c = conn.cursor()

    c.execute("SELECT name, party, votes_count FROM candidates ORDER BY votes_count DESC")
    results = c.fetchall()

    conn.close()

    if results:
        df = pd.DataFrame(results, columns=["Candidate", "Party", "Votes"])

        fig = px.bar(
            df,
            x="Candidate",
            y="Votes",
            color="Party",
            color_discrete_sequence=["#6c63ff", "#48cae4", "#ff6b6b"],
            template="plotly_dark"
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="home_chart"
    )