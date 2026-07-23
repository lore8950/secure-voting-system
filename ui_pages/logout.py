import streamlit as st

def logout_page():

    st.session_state["logged_in"] = False
    st.session_state["admin_logged_in"] = False
    st.session_state["user"] = None
    st.session_state["role"] = None
    st.session_state["has_voted"] = 0
    st.session_state["menu"] = "🏠 Home"

    st.success("✅ Logout Successful!")
    st.info("Redirecting to Home...")

    st.rerun()