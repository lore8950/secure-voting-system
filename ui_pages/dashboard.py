import streamlit as st

def dashboard_page():

    st.title("🏠 User Dashboard")

    st.success(f"Welcome {st.session_state['user']}")

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"👤 Username : {st.session_state['user']}")

    with col2:
        st.info(f"🎭 Role : {st.session_state['role']}")

    st.markdown("---")
    st.write("Select an option from the sidebar.")