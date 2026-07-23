import streamlit as st
import sqlite3
import os


def candidates_page():

    st.title("👤 Candidate Management")

    # -----------------------------
    # Add Candidate
    # -----------------------------

    st.subheader("➕ Add Candidate")

    name = st.text_input("Candidate Name")
    party = st.text_input("Party Name")

    photo = st.file_uploader(
        "Candidate Photo",
        type=["jpg", "jpeg", "png"]
    )

    if st.button("Add Candidate"):

        if not name or not party:
            st.warning("Fill all fields.")
            return

        photo_path = None

        if photo:

            os.makedirs("candidate_images", exist_ok=True)

            ext = os.path.splitext(photo.name)[1]

            photo_path = os.path.join(
                "candidate_images",
                f"{name}{ext}"
            )

            with open(photo_path, "wb") as f:
                f.write(photo.getbuffer())

        conn = sqlite3.connect("secure_voting.db")
        c = conn.cursor()

        try:

            c.execute(
                """
                INSERT INTO candidates(name,party,photo_path)
                VALUES(?,?,?)
                """,
                (name, party, photo_path)
            )

            conn.commit()

            st.success("Candidate Added Successfully")

            st.rerun()

        except sqlite3.IntegrityError:

            st.error("Candidate already exists.")

        conn.close()

    st.markdown("---")

    # -----------------------------
    # Candidate List
    # -----------------------------

    st.subheader("📋 Candidate List")

    conn = sqlite3.connect("secure_voting.db")
    c = conn.cursor()

    c.execute("""
        SELECT
        id,
        name,
        party,
        votes_count,
        photo_path
        FROM candidates
        ORDER BY id
    """)

    candidates = c.fetchall()

    conn.close()

    if not candidates:

        st.info("No Candidate Available")

        return

    for cid, name, party, votes, photo in candidates:

        col1, col2, col3 = st.columns([1,4,1])

        with col1:

            if photo and os.path.exists(photo):
                st.image(photo, width=80)

        with col2:

            st.markdown(f"### {name}")
            st.write(f"🏛 Party : {party}")
            st.write(f"🗳 Votes : {votes}")

        with col3:

            if st.button("🗑 Delete", key=f"delete_{cid}"):

                if photo and os.path.exists(photo):
                    os.remove(photo)

                conn = sqlite3.connect("secure_voting.db")
                c = conn.cursor()

                c.execute(
                    "DELETE FROM candidates WHERE id=?",
                    (cid,)
                )

                conn.commit()
                conn.close()

                st.success("Candidate Deleted")

                st.rerun()

    st.markdown("---")

    # -----------------------------
    # Edit Candidate
    # -----------------------------

    st.subheader("✏️ Edit Candidate")

    conn = sqlite3.connect("secure_voting.db")
    c = conn.cursor()

    c.execute(
        "SELECT id,name FROM candidates ORDER BY id"
    )

    rows = c.fetchall()

    conn.close()

    candidate_dict = {
        f"{name} (ID:{cid})": cid
        for cid, name in rows
    }

    if candidate_dict:

        selected = st.selectbox(
            "Select Candidate",
            list(candidate_dict.keys())
        )

        cid = candidate_dict[selected]

        conn = sqlite3.connect("secure_voting.db")
        c = conn.cursor()

        c.execute("""
            SELECT
            name,
            party,
            photo_path
            FROM candidates
            WHERE id=?
        """,(cid,))

        old_name, old_party, old_photo = c.fetchone()

        conn.close()

        new_name = st.text_input(
            "New Name",
            value=old_name
        )

        new_party = st.text_input(
            "New Party",
            value=old_party
        )

        new_photo = st.file_uploader(
            "New Photo",
            type=["jpg","jpeg","png"]
        )

        if st.button("Update Candidate"):

            photo_path = old_photo

            if new_photo:

                os.makedirs(
                    "candidate_images",
                    exist_ok=True
                )

                if old_photo and os.path.exists(old_photo):
                    os.remove(old_photo)

                ext = os.path.splitext(new_photo.name)[1]

                photo_path = os.path.join(
                    "candidate_images",
                    f"{new_name}{ext}"
                )

                with open(photo_path,"wb") as f:
                    f.write(new_photo.getbuffer())

            conn = sqlite3.connect("secure_voting.db")
            c = conn.cursor()

            c.execute("""
                UPDATE candidates
                SET
                name=?,
                party=?,
                photo_path=?
                WHERE id=?
            """,
            (
                new_name,
                new_party,
                photo_path,
                cid
            ))

            conn.commit()
            conn.close()

            st.success("Candidate Updated")

            st.rerun()