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

    # ---------------- Header ----------------

    h1, h2, h3, h4 = st.columns([3, 2, 2, 1.5])

    h1.markdown("**👤 Username**")
    h2.markdown("**Role**")
    h3.markdown("**Voted**")
    h4.markdown("**Action**")

    st.markdown("---")

    # ---------------- User List ----------------

    for uname, role, has_voted in users:

        voted = "✅ Yes" if has_voted else "❌ No"

        col1, col2, col3, col4 = st.columns([3, 2, 2, 1.5])

        with col1:
            st.write(uname)

        with col2:
            st.write(role)

        with col3:
            st.write(voted)

        with col4:

            if st.button(
                "🗑️",
                key=f"del_{uname}",
                help=f"Delete {uname}",
                use_container_width=True
            ):

                conn = sqlite3.connect("secure_voting.db")
                c = conn.cursor()

                # Face image delete
                c.execute(
                    "SELECT face_img_path FROM users WHERE username=?",
                    (uname,)
                )

                row = c.fetchone()

                if row and row[0]:
                    if os.path.exists(row[0]):
                        os.remove(row[0])

                # Delete user
                c.execute(
                    "DELETE FROM users WHERE username=?",
                    (uname,)
                )

                conn.commit()
                conn.close()

                st.success(f"✅ {uname} deleted successfully.")

                st.rerun()
