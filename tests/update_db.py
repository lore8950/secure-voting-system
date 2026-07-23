import sqlite3

conn = sqlite3.connect("secure_voting.db")
c = conn.cursor()

try:
    c.execute("ALTER TABLE users ADD COLUMN otp_salt TEXT")
    print("✅ otp_salt column added successfully.")
except sqlite3.OperationalError as e:
    print("⚠️", e)

conn.commit()
conn.close()