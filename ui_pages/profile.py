import streamlit as st
import sqlite3
import os

def profile_page():

    st.title("👤 My Profile")

    conn = sqlite3.connect("secure_voting.db")
    c = conn.cursor()

    c.execute("""
        SELECT username, email, role, face_img_path
        FROM users
        WHERE username=?
    """, (st.session_state["user"],))

    user = c.fetchone()

    conn.close()

    if user:

        username, email, role, face_path = user

        col1, col2 = st.columns([1,2])

        with col1:

            if face_path and os.path.exists(face_path):
                st.image(face_path, width=180)
            else:
                st.info("No Face Image")

        with col2:

            st.text_input("Username", username, disabled=True)
            st.text_input("Email", email, disabled=True)
            st.text_input("Role", role, disabled=True)