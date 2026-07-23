import streamlit as st

def admin_logout_page():

    st.session_state["admin_logged_in"] = False
    st.session_state["menu"] = "🏠 Home"

    st.success("✅ Admin Logged Out")

    st.rerun()