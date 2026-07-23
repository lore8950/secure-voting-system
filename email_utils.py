import smtplib
import traceback
from email.message import EmailMessage

SENDER_EMAIL = "apurbodebnath809@gmail.com"

with open("app_password.txt", "r") as f:
    APP_PASSWORD = f.read().strip()


def send_otp(receiver_email, otp):
    print("=" * 50)
    print("Sending OTP to:", receiver_email)

    msg = EmailMessage()
    msg["Subject"] = "Secure Voting System - OTP Verification"
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email

    msg.set_content(f"""
Hello,

Your OTP for Secure Voting System is:

{otp}

This OTP is valid for one login only.

Do not share it with anyone.

Thank you.
""")

    try:
        print("Connecting to Gmail...")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            print("Login successful.")

            smtp.send_message(msg)
            print("Email sent successfully.")

        return True

    except Exception as e:
        traceback.print_exc()
        print("Email Error:", e)
        return False