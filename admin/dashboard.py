import streamlit as st
import sqlite3

def admin_dashboard():

    conn = sqlite3.connect("secure_voting.db")
    c = conn.cursor()

    # Dashboard Statistics
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users WHERE role='Voter'")
    total_voters = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM candidates")
    total_candidates = c.fetchone()[0]

    c.execute("SELECT SUM(votes_count) FROM candidates")
    total_votes = c.fetchone()[0] or 0

    conn.close()

    st.subheader("📊 Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("👥 Users", total_users)
    col2.metric("🗳️ Voters", total_voters)
    col3.metric("🎯 Candidates", total_candidates)
    col4.metric("✅ Votes", total_votes)

    st.markdown("---")