import sqlite3
import time

DB_NAME = "secure_voting.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        verification_code TEXT,
        otp_salt TEXT,
        face_img_path TEXT,
        has_voted INTEGER DEFAULT 0
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS candidates(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        party TEXT NOT NULL,
        votes_count INTEGER DEFAULT 0,
        photo_path TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS election_settings(
        id INTEGER PRIMARY KEY,
        end_time REAL,
        is_active INTEGER DEFAULT 1
    )
    """)

    c.execute("SELECT COUNT(*) FROM candidates")

    if c.fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO candidates(name,party) VALUES(?,?)",
            [
                ("Candidate A", "Party Blue"),
                ("Candidate B", "Party Green"),
                ("Candidate C", "Party Red"),
            ],
        )

    c.execute("SELECT COUNT(*) FROM election_settings")

    if c.fetchone()[0] == 0:
        c.execute(
            """
            INSERT INTO election_settings
            (id,end_time,is_active)
            VALUES(1,?,1)
            """,
            (time.time() + 3600,),
        )

    conn.commit()
    conn.close()


def get_election_settings():
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "SELECT end_time,is_active FROM election_settings WHERE id=1"
    )

    row = c.fetchone()

    conn.close()

    return row


def set_election_end_time(hours):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        """
        UPDATE election_settings
        SET end_time=?,is_active=1
        WHERE id=1
        """,
        (time.time() + hours * 3600,),
    )

    conn.commit()
    conn.close()


def toggle_election(active):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        """
        UPDATE election_settings
        SET is_active=?
        WHERE id=1
        """,
        (1 if active else 0,),
    )

    conn.commit()
    conn.close()


def is_election_active():
    row = get_election_settings()

    if not row:
        return False

    end_time, active = row

    return bool(active) and time.time() < end_time


def get_remaining_time():
    row = get_election_settings()

    if not row:
        return 0

    return max(0, row[0] - time.time())