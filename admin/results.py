import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

def admin_results_page():

    st.title("📈 Election Results")

    conn = sqlite3.connect("secure_voting.db")
    c = conn.cursor()

    c.execute("""
        SELECT name, party, votes_count
        FROM candidates
        ORDER BY votes_count DESC
    """)

    results = c.fetchall()
    conn.close()

    if not results:
        st.info("No results available.")
        return

    df = pd.DataFrame(
        results,
        columns=["Candidate", "Party", "Votes"]
    )

    # Pie Chart
    fig1 = px.pie(
        df,
        values="Votes",
        names="Candidate",
        hole=0.4,
        template="plotly_dark"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    # Bar Chart
    fig2 = px.bar(
        df,
        x="Candidate",
        y="Votes",
        color="Party",
        text="Votes",
        template="plotly_dark"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.subheader("🏆 Final Result")

    st.dataframe(
        df,
        use_container_width=True
    )