import streamlit as st
import sqlite3
import os

from security_utils import verify_password
from otp_utils import verify_otp
from face_utils import verify_faces

def login_page():
    st.header("🔐 Secure Identity Login")
    uname = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    v_code = st.text_input("6-Digit OTP")
    img_file = st.camera_input("📸 Verify Your Face")

    if st.button("Secure Log In", type="primary"):
        if uname and pwd and v_code and img_file:
            conn = sqlite3.connect("secure_voting.db")
            c = conn.cursor()
            c.execute("""
                SELECT password, role, verification_code, otp_salt,
                       face_img_path, has_voted
                FROM users
                WHERE username=?
            """, (uname,))
            user = c.fetchone()
            conn.close()

            if user:
                db_pwd_hash, role, db_otp_hash, db_otp_salt, db_face_path, has_voted = user

                if not verify_password(pwd, db_pwd_hash):
                    st.error("❌ Incorrect Username or Password!")

                elif not verify_otp(v_code, db_otp_hash, db_otp_salt):
                    st.error("❌ Incorrect OTP!")

                else:
                    # Save live image temporarily
                    with open("temp_live.jpg", "wb") as f:
                        f.write(img_file.getbuffer())

                    matched = verify_faces(db_face_path, "temp_live.jpg")

                    # Delete temporary image
                    if os.path.exists("temp_live.jpg"):
                        os.remove("temp_live.jpg")

                    if matched:
                        st.success(f"✅ Welcome **{uname}**!")

                        st.session_state["logged_in"] = True
                        st.session_state["user"] = uname
                        st.session_state["role"] = role
                        st.session_state["has_voted"] = has_voted
                        st.session_state["menu"] = "🏠 Dashboard"

                        st.rerun()
                    else:
                        st.error("❌ Face Match Failed!")

            else:
                st.error("❌ Incorrect Username or Password!")