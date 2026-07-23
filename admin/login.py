import streamlit as st
from security_utils import verify_admin_password


def admin_login_page():

    st.title("🛡️ Admin Login")

    admin_pass = st.text_input(
        "Admin Password",
        type="password"
    )

    if st.button("Login"):

        if verify_admin_password(admin_pass):

            st.session_state["admin_logged_in"] = True
            st.session_state["logged_in"] = False
            st.session_state["menu"] = "📊 Dashboard"

            st.success("Login Successful")

            st.rerun()

        else:
            st.error("Wrong Admin Password")