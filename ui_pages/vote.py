import streamlit as st
import sqlite3
import os
import time

from database import is_election_active

def vote_page():
    if "user" in st.session_state:
            st.markdown("---")
            st.info(
                f"👤 **{st.session_state['user']}** | Role: **{st.session_state['role']}**"
            )
    
            if st.session_state["role"] == "Voter":
                if not is_election_active():
                    st.error("⏰ Election is closed! Voting is not allowed.")
    
                elif st.session_state["has_voted"] == 1:
                    st.error("⚠️ You have already voted!")
    
                else:
                    st.subheader("🗳️ Cast Your Vote")
    
                    conn = sqlite3.connect("secure_voting.db")
                    c = conn.cursor()
    
                    c.execute("""
                        SELECT id, name, party, photo_path
                        FROM candidates
                        ORDER BY id
                    """)
    
                    candidates = c.fetchall()
                    conn.close()
    
                    options = {}
    
                    st.markdown("## 👥 Candidates")
    
                    for c_id, name, party, photo_path in candidates:
    
                        st.markdown("---")
    
                        col1, col2 = st.columns([1, 3])
    
                        with col1:
                            if photo_path and os.path.exists(photo_path):
                                st.image(photo_path, width=120)
                            else:
                                st.write("📷 No Photo")
    
                        with col2:
                            st.markdown(f"### 👤 {name}")
                            st.write(f"🏛️ Party: **{party}**")
    
                        options[f"{name} ({party})"] = c_id
    
                    st.markdown("---")
    
                    selected = st.radio(
                        "✅ Select Your Candidate",
                        list(options.keys())
                    )
    
                    if st.button("🗳️ Cast Vote", type="primary"):
    
                        candidate_id = options[selected]
    
                        conn = sqlite3.connect("secure_voting.db")
                        c = conn.cursor()
    
                        c.execute(
                            """
                            UPDATE users
                            SET has_voted = 1
                            WHERE username = ?
                            """,
                            (st.session_state["user"],)
                        )
    
                        c.execute(
                            """
                            UPDATE candidates
                            SET votes_count = votes_count + 1
                            WHERE id = ?
                            """,
                            (candidate_id,)
                        )
    
                        conn.commit()
                        conn.close()
    
                        st.success("🎉 Vote Successfully Counted!")
    
                        st.session_state["has_voted"] = 1
    
                        st.balloons()
    
                        time.sleep(1)
    
                        st.rerun()