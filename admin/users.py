import streamlit as st
import sqlite3
import os

def users_page():

    st.title("👥 Users")

    conn = sqlite3.connect("secure_voting.db")
    c = conn.cursor()

    c.execute("""
        SELECT username, role, has_voted
        FROM users
        ORDER BY role, username
    """)

    users = c.fetchall()
    conn.close()

    if not users:
        st.info("No users found.")
        return

    # Header
    h1, h2, h3, h4 = st.columns([3, 2, 2, 1])
    h1.markdown("**👤 Username**")
    h2.markdown("**Role**")
    h3.markdown("**Voted**")
    h4.markdown("**Action**")

    st.markdown("---")

    for uname, role, has_voted in users:

        voted = "✅ Yes" if has_voted else "❌ No"

        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

        col1.write(uname)
        col2.write(role)
        col3.write(voted)

        with col4:

            if st.button("🗑 Delete", key=f"del_{uname}"):

                conn = sqlite3.connect("secure_voting.db")
                c = conn.cursor()

                c.execute(
                    "SELECT face_img_path FROM users WHERE username=?",
                    (uname,)
                )

                row = c.fetchone()

                if row and row[0] and os.path.exists(row[0]):
                    os.remove(row[0])

                c.execute(
                    "DELETE FROM users WHERE username=?",
                    (uname,)
                )

                conn.commit()
                conn.close()

                st.success(f"{uname} deleted successfully.")

                st.rerun()