# ─── REGISTER ──────────────────────────────────────────────────────────
import streamlit as st
import sqlite3
import time

from email_utils import send_otp
from face_utils import save_face
from otp_utils import generate_otp, hash_otp_for_storage
from security_utils import hash_password, is_strong_password
def register_page():

    st.header("📝 Account Registration")


    uname = st.text_input("Username")
    email = st.text_input("Email Address")
    pwd = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["Voter", "Candidate", "Audience"])
    img_file = st.camera_input("📸 Capture Face Photo")

    if st.button("Complete Registration", type="primary"):

        if uname and email and pwd and img_file:

            # Password Strength Check
            if not is_strong_password(pwd):
                st.error("""
❌ Password must contain:

✔ At least 8 characters
✔ One uppercase letter (A-Z)
✔ One lowercase letter (a-z)
✔ One number (0-9)
✔ One special character (@$!%*?&)
                """)
                st.stop()

            img_path = save_face(img_file, uname)

            # Hash Password
            hashed_pwd = hash_password(pwd)

            # Generate OTP
            plain_otp = generate_otp()
            otp_hash, otp_salt = hash_otp_for_storage(plain_otp)

            try:
                conn = sqlite3.connect("secure_voting.db")
                c = conn.cursor()

                c.execute("""
INSERT INTO users
(username, email, password, role, verification_code, otp_salt, face_img_path)
VALUES (?,?,?,?,?,?,?)
""",
(
    uname,
    email,
    hashed_pwd,
    role,
    otp_hash,
    otp_salt,
    img_path
))

                conn.commit()
                conn.close()

                # Send OTP to Gmail
                if send_otp(email, plain_otp):
                    st.success("🎉 Registered Successfully!")
                    st.success("📧 OTP has been sent to your Gmail.")
                else:
                    st.warning("⚠️ Registration successful, but OTP email could not be sent.")

                st.info("➡ Redirecting to Login Page...")

                time.sleep(2)

                st.session_state["last_username"] = uname
                st.session_state["menu"] = "🔐 Login"

                st.rerun()

            except sqlite3.IntegrityError:
                st.error("❌ Username or Email already exists!")

        else:
            st.error("❌ Fill all fields and capture face!")
