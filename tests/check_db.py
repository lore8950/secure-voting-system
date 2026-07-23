import sqlite3

conn = sqlite3.connect("secure_voting.db")
c = conn.cursor()

print("=== USERS TABLE COLUMNS ===")
c.execute("PRAGMA table_info(users)")
for col in c.fetchall():
    print(col)

print("\n=== CREATE TABLE SQL ===")
c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
print(c.fetchone()[0])

conn.close()