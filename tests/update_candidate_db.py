import sqlite3

conn = sqlite3.connect("../secure_voting.db")
c = conn.cursor()

try:
    c.execute("ALTER TABLE candidates ADD COLUMN photo_path TEXT")
    print("✅ photo_path column added successfully.")
except sqlite3.OperationalError as e:
    print("⚠️", e)

conn.commit()
conn.close()