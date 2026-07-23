import sqlite3

conn = sqlite3.connect("../secure_voting.db")
c = conn.cursor()

c.execute("SELECT id, name, party, photo_path FROM candidates")

rows = c.fetchall()

print("\n=== Candidates ===\n")

for row in rows:
    print(row)

conn.close()