
import streamlit as st
import sqlite3
import os
import time
import pandas as pd
import plotly.express as px
from email_utils import send_otp


from face_utils import save_face, verify_faces
from otp_utils import generate_otp, hash_otp_for_storage, verify_otp
from security_utils import (
    hash_password,
    verify_password,
    verify_admin_password,
    is_strong_password
)

from database import (
    init_db,
    get_connection,
    get_election_settings,
    set_election_end_time,
    toggle_election,
    is_election_active,
    get_remaining_time
)

# ─── CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0c1222; }
    .stApp { background: radial-gradient(circle at 85% -10%, #19345a 0%, #101b32 36%, #0c1222 75%); }
    h1, h2, h3 { color: #f7faff !important; }
    .stTextInput > label, .stSelectbox > label, .stRadio > label { color: #b8c6dd !important; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #101a2f 0%, #0b1324 100%);
        border-right: 1px solid rgba(148, 163, 184, .16);
    }
    [data-testid="stSidebar"] > div:first-child { padding: 1.25rem .9rem; }
    [data-testid="stSidebar"] .stRadio > div { gap: .32rem; }
    [data-testid="stSidebar"] .stRadio label {
        width: 100%; border-radius: 10px; padding: .45rem .6rem;
        color: #cbd5e1 !important; font-size: .92rem; transition: .18s ease;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(96, 165, 250, .12); color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stRadio input { display: none; }
    [data-testid="stSidebar"] .stRadio label:has(input:checked) {
        color: #ffffff !important; font-weight: 600;
        background: linear-gradient(90deg, rgba(59, 130, 246, .28), rgba(34, 211, 238, .13));
        box-shadow: inset 3px 0 0 #38bdf8;
    }
    .sidebar-brand {
        padding: .25rem .55rem 1.1rem; margin-bottom: .5rem;
        border-bottom: 1px solid rgba(148, 163, 184, .14);
    }
    .sidebar-brand .eyebrow { color: #38bdf8; font-size: .72rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
    .sidebar-brand h2 { margin: .28rem 0 .2rem; font-size: 1.25rem !important; }
    .sidebar-brand p { margin: 0; color: #94a3b8; font-size: .8rem; }
    .nav-label { color: #71809a; font-size: .7rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; margin: .85rem .55rem .35rem; }
    .stButton > button {
        background: linear-gradient(90deg, #6c63ff, #48cae4);
        color: white; border: none; border-radius: 10px;
        padding: 0.5rem 2rem; font-weight: bold;
        transition: transform 0.2s;
    }
    .stButton > button:hover { transform: scale(1.05); }
    .stSuccess { background-color: #1a3a2a !important; border-left: 4px solid #00c896 !important; }
    .stError   { background-color: #3a1a1a !important; border-left: 4px solid #ff6b6b !important; }
    .stWarning { background-color: #3a3a1a !important; border-left: 4px solid #ffd93d !important; }
    .metric-card {
        background: linear-gradient(135deg, #1e1e3f, #2a2a5a);
        border-radius: 15px; padding: 20px; margin: 10px 0;
        border: 1px solid #3a3a7a; text-align: center;
    }
    .metric-card h2 { font-size: 2.5rem !important; color: #6c63ff !important; }
    .metric-card p  { color: #a0a0cc; margin: 0; }
    .voter-card {
        background: #1e1e3f; border-radius: 10px;
        padding: 10px 15px; margin: 5px 0;
        border-left: 3px solid #6c63ff;
        color: #e0e0ff;
    }
    .timer-box {
        background: linear-gradient(135deg, rgba(30, 64, 175, .3), rgba(14, 116, 144, .22));
        border-radius: 12px; padding: 13px;
        border: 1px solid rgba(56, 189, 248, .4); text-align: center;
        margin: 1.25rem .2rem .25rem;
    }
    .timer-box h1 { font-size: 1.7rem !important; color: #f8fafc !important; margin: .2rem 0 !important; }
    .timer-box p  { color: #b7cce7; margin: 0; font-size: .78rem; }
</style>
""", unsafe_allow_html=True)

# ─── DB ────────────────────────────────────────────────────────────────

init_db()

# ─── HEADER ────────────────────────────────────────────────────────────
st.markdown("<h1 style='text-align:center;'>🗳️ Smart Voting System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#a0a0cc;'>Secure • Transparent • Efficient</p>", unsafe_allow_html=True)
st.markdown("---")

# ─── SIDEBAR ───────────────────────────────────────────────────────────

# Session State
if "menu" not in st.session_state:
    st.session_state["menu"] = "🏠 Home"

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

if "user" not in st.session_state:
    st.session_state["user"] = None

with st.sidebar:

    st.markdown("""
    <div class='sidebar-brand'>
        <div class='eyebrow'>Secure platform</div>
        <h2>🗳️ VoteSphere</h2>
        <p>Digital election portal</p>
    </div>
    <div class='nav-label'>Workspace</div>
    """, unsafe_allow_html=True)

    # -------------------------------
    # Navigation Menu
    # -------------------------------

    if not st.session_state["logged_in"] and not st.session_state["is_admin"]:

        menu = [
            "🏠 Home",
            "📝 Register",
            "🔐 Login",
            "🛡️ Admin Panel"
        ]

    elif st.session_state["logged_in"]:

        menu = [
            "🏠 Dashboard",
            "👤 Profile",
            "🗳️ Vote",
            "📊 Results",
            "🚪 Logout"
        ]

    elif st.session_state["is_admin"]:

        menu = [
            "📊 Dashboard",
            "👥 Users",
            "👤 Candidates",
            "⏱ Election",
            "📈 Results",
            "🚪 Logout"
        ]

    if st.session_state["menu"] not in menu:
        st.session_state["menu"] = menu[0]

    choice = st.radio(
        "Navigation",
        menu,
        index=menu.index(st.session_state["menu"]),
        label_visibility="collapsed"
    )

    st.session_state["menu"] = choice

    # -------------------------------
    # Election Timer
    # -------------------------------

    rem = get_remaining_time()

    if rem > 0 and is_election_active():

        h, r = divmod(int(rem), 3600)
        m, s = divmod(r, 60)

        st.markdown(f"""
        <div class='timer-box'>
            <p>● LIVE ELECTION · ENDS IN</p>
            <h1>{h:02d}:{m:02d}:{s:02d}</h1>
        </div>
        """, unsafe_allow_html=True)

    else:

        st.markdown("""
        <div class='timer-box'>
            <p>ELECTION STATUS</p>
            <h1>● Closed</h1>
        </div>
        """, unsafe_allow_html=True)

# ─── HOME ──────────────────────────────────────────────────────────────
if choice == "🏠 Home":
    conn = sqlite3.connect("secure_voting.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE role='Voter'")
    total_voters = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE has_voted=1")
    voted = c.fetchone()[0]
    c.execute("SELECT SUM(votes_count) FROM candidates")
    total_votes = c.fetchone()[0] or 0
    conn.close()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-card'><h2>{total_voters}</h2><p>Total Voters</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><h2>{voted}</h2><p>Votes Cast</p></div>", unsafe_allow_html=True)
    with col3:
        pct = round((voted / total_voters * 100) if total_voters > 0 else 0, 1)
        st.markdown(f"<div class='metric-card'><h2>{pct}%</h2><p>Turnout</p></div>", unsafe_allow_html=True)

    st.markdown("### 🏆 Current Standing")
    conn = sqlite3.connect("secure_voting.db")
    c = conn.cursor()
    c.execute("SELECT name, party, votes_count FROM candidates ORDER BY votes_count DESC")
    results = c.fetchall()
    conn.close()
    if results:
        df = pd.DataFrame(results, columns=["Candidate", "Party", "Votes"])
        fig = px.bar(df, x="Candidate", y="Votes", color="Party",
                     color_discrete_sequence=["#6c63ff", "#48cae4", "#ff6b6b"],
                     template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

# ─── REGISTER ──────────────────────────────────────────────────────────
elif choice == "📝 Register":
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

# ─── LOGIN ─────────────────────────────────────────────────────────────
elif choice == "🔐 Login":
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
                        st.session_state["user"] = uname
                        st.session_state["role"] = role
                        st.session_state["has_voted"] = has_voted
                        st.session_state.logged_in = True
                        st.session_state.menu = "🏠 Dashboard"

                        st.rerun()
                    else:
                        st.error("❌ Face Match Failed!")

            else:
                st.error("❌ Incorrect Username or Password!")

    # if "user" in st.session_state:
    #     st.markdown("---")
    #     st.info(
    #         f"👤 **{st.session_state['user']}** | Role: **{st.session_state['role']}**"
    #     )

    #     if st.session_state["role"] == "Voter":
    #         if not is_election_active():
    #             st.error("⏰ Election is closed! Voting is not allowed.")

    #         elif st.session_state["has_voted"] == 1:
    #             st.error("⚠️ You have already voted!")

    #         else:
    #             st.subheader("🗳️ Cast Your Vote")

    #             conn = sqlite3.connect("secure_voting.db")
    #             c = conn.cursor()

    #             c.execute("""
    #                 SELECT id, name, party, photo_path
    #                 FROM candidates
    #                 ORDER BY id
    #             """)

    #             candidates = c.fetchall()
    #             conn.close()

    #             options = {}

    #             st.markdown("## 👥 Candidates")

    #             for c_id, name, party, photo_path in candidates:

    #                 st.markdown("---")

    #                 col1, col2 = st.columns([1, 3])

    #                 with col1:
    #                     if photo_path and os.path.exists(photo_path):
    #                         st.image(photo_path, width=120)
    #                     else:
    #                         st.write("📷 No Photo")

    #                 with col2:
    #                     st.markdown(f"### 👤 {name}")
    #                     st.write(f"🏛️ Party: **{party}**")

    #                 options[f"{name} ({party})"] = c_id

    #             st.markdown("---")

    #             selected = st.radio(
    #                 "✅ Select Your Candidate",
    #                 list(options.keys())
    #             )

    #             if st.button("🗳️ Cast Vote", type="primary"):

    #                 candidate_id = options[selected]

    #                 conn = sqlite3.connect("secure_voting.db")
    #                 c = conn.cursor()

    #                 c.execute(
    #                     """
    #                     UPDATE users
    #                     SET has_voted = 1
    #                     WHERE username = ?
    #                     """,
    #                     (st.session_state["user"],)
    #                 )

    #                 c.execute(
    #                     """
    #                     UPDATE candidates
    #                     SET votes_count = votes_count + 1
    #                     WHERE id = ?
    #                     """,
    #                     (candidate_id,)
    #                 )

    #                 conn.commit()
    #                 conn.close()

    #                 st.success("🎉 Vote Successfully Counted!")

    #                 st.session_state["has_voted"] = 1

    #                 st.balloons()

    #                 time.sleep(1)

    #                 st.rerun()

# ─── USER DASHBOARD ─────────────────────────────────────────
elif choice == "🏠 Dashboard":

    st.title("🏠 User Dashboard")

    st.success(f"Welcome {st.session_state['user']}")

    col1, col2 = st.columns(2)

    with col1:
        st.info(f"👤 Username : {st.session_state['user']}")

    with col2:
        st.info(f"🎭 Role : {st.session_state['role']}")

    st.markdown("---")
    st.write("Select an option from the sidebar.")

# ─── RESULTS ───────────────────────────────────────────────────────────
elif choice == "📊 Results":
    st.header("📊 Election Results")
    conn = sqlite3.connect("secure_voting.db")
    c = conn.cursor()
    c.execute("SELECT name, party, votes_count FROM candidates ORDER BY votes_count DESC")
    results = c.fetchall()
    conn.close()

    if results:
        df = pd.DataFrame(results, columns=["Candidate", "Party", "Votes"])
        total = df["Votes"].sum()

        fig_pie = px.pie(df, values="Votes", names="Candidate",
                         color_discrete_sequence=["#6c63ff", "#48cae4", "#ff6b6b"],
                         template="plotly_dark", hole=0.4)
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_pie, use_container_width=True)

        fig_bar = px.bar(df, x="Candidate", y="Votes", color="Party", text="Votes",
                         color_discrete_sequence=["#6c63ff", "#48cae4", "#ff6b6b"],
                         template="plotly_dark")
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("### 🏅 Leaderboard")
        for i, (name, party, votes) in enumerate(results):
            medal = ["🥇", "🥈", "🥉"][i] if i < 3 else "🔹"
            pct = round(votes / total * 100, 1) if total > 0 else 0
            st.markdown(f"<div class='voter-card'>{medal} <b>{name}</b> ({party}) — {votes} votes ({pct}%)</div>",
                        unsafe_allow_html=True)

# ─── VOTER LIST ────────────────────────────────────────────────────────
elif choice == "👥 Voter List":
    st.header("👥 Voter List")
    conn = sqlite3.connect("secure_voting.db")
    c = conn.cursor()
    c.execute("SELECT username, role, has_voted FROM users ORDER BY role, username")
    users = c.fetchall()
    conn.close()

    search = st.text_input("🔍 Search by name")
    filter_role = st.selectbox("Filter by Role", ["All", "Voter", "Candidate", "Audience"])

    voted_count   = sum(1 for _, _, v in users if v == 1)
    pending_count = sum(1 for _, r, v in users if r == "Voter" and v == 0)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='metric-card'><h2>{voted_count}</h2><p>Voted</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><h2>{pending_count}</h2><p>Pending</p></div>", unsafe_allow_html=True)

    st.markdown("---")
    for uname, role, has_voted in users:
        if search and search.lower() not in uname.lower():
            continue
        if filter_role != "All" and role != filter_role:
            continue
        status = "✅ Voted" if has_voted else "⏳ Pending"
        color  = "#00c896" if has_voted else "#ffd93d"
        st.markdown(f"<div class='voter-card'>👤 <b>{uname}</b> | {role} | <span style='color:{color}'>{status}</span></div>",
                    unsafe_allow_html=True)

# ─────────────────────────────────────────────────────
# ADMIN PANEL
# ─────────────────────────────────────────────────────
elif choice == "🛡️ Admin Panel":

    st.header("🛡️ Admin Panel")

    admin_pass = st.text_input(
        "Admin Password",
        type="password"
    )

    if admin_pass:

        if verify_admin_password(admin_pass):

            st.success("✅ Admin Access Granted")

            conn = sqlite3.connect("secure_voting.db")
            c = conn.cursor()

            # Dashboard
            c.execute("SELECT COUNT(*) FROM users")
            total_users = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM users WHERE role='Voter'")
            total_voters = c.fetchone()[0]

            c.execute("SELECT COUNT(*) FROM candidates")
            total_candidates = c.fetchone()[0]

            c.execute("SELECT SUM(votes_count) FROM candidates")
            total_votes = c.fetchone()[0] or 0

            conn.close()

            st.subheader("📊 Dashboard")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("👥 Users", total_users)
            col2.metric("🗳️ Voters", total_voters)
            col3.metric("🎯 Candidates", total_candidates)
            col4.metric("✅ Votes", total_votes)

            st.markdown("---")

            # Election Timer

            st.subheader("⏱ Election Control")

            row = get_election_settings()

            active = bool(row[1])

            col1, col2 = st.columns(2)

            with col1:

                hours = st.number_input(
                    "Duration (Hours)",
                    min_value=0.5,
                    max_value=72.0,
                    value=1.0
                )

                if st.button("🕐 Set Timer"):

                    set_election_end_time(hours)

                    st.success("Timer Updated")

            with col2:

                if active:

                    if st.button("🔴 Stop Election"):

                        toggle_election(False)

                        st.success("Election Stopped")

                        st.rerun()

                else:

                    if st.button("🟢 Start Election"):

                        toggle_election(True)

                        st.success("Election Started")

                        st.rerun()

            st.markdown("---")

            # Reset Votes

            st.subheader("🔄 Reset Votes")

            if st.button("⚠ Reset All Votes"):

                conn = sqlite3.connect("secure_voting.db")
                c = conn.cursor()

                c.execute("UPDATE candidates SET votes_count=0")
                c.execute("UPDATE users SET has_voted=0")

                conn.commit()
                conn.close()

                st.success("Votes Reset Successfully")

            st.markdown("---")

            # Add Candidate

            st.subheader("➕ Add Candidate")

            name = st.text_input("Candidate Name")

            party = st.text_input("Party Name")

            photo = st.file_uploader(
                "Candidate Photo",
                type=["jpg","jpeg","png"]
            )

            if st.button("Add Candidate"):

                if name and party:

                    photo_path = None

                    if photo:

                        os.makedirs(
                            "candidate_images",
                            exist_ok=True
                        )

                        ext = os.path.splitext(photo.name)[1]

                        photo_path = os.path.join(
                            "candidate_images",
                            f"{name}{ext}"
                        )

                        with open(photo_path,"wb") as f:
                            f.write(photo.getbuffer())

                    conn = sqlite3.connect("secure_voting.db")
                    c = conn.cursor()

                    try:

                        c.execute(
                            """
                            INSERT INTO candidates
                            (name,party,photo_path)
                            VALUES(?,?,?)
                            """,
                            (
                                name,
                                party,
                                photo_path
                            )
                        )

                        conn.commit()

                        st.success("Candidate Added")

                        st.rerun()

                    except sqlite3.IntegrityError:

                        st.error("Candidate already exists")

                    conn.close()

            st.markdown("---")

            # Candidate List

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

            if len(candidates)==0:

                st.info("No Candidates")

            else:

                for cid,name,party,votes,photo in candidates:

                    col1,col2,col3 = st.columns([1,4,1])

                    with col1:

                        if photo and os.path.exists(photo):

                            st.image(photo,width=80)

                    with col2:

                        st.markdown(f"### {name}")

                        st.write(f"🏛 Party : {party}")

                        st.write(f"🗳 Votes : {votes}")

                    with col3:

                        if st.button(
                            "🗑 Delete",
                            key=f"del_{cid}"
                        ):

                            if photo and os.path.exists(photo):

                                os.remove(photo)

                            conn = sqlite3.connect(
                                "secure_voting.db"
                            )

                            c = conn.cursor()

                            c.execute(
                                "DELETE FROM candidates WHERE id=?",
                                (cid,)
                            )

                            conn.commit()

                            conn.close()

                            st.success(
                                f"{name} Deleted"
                            )

                            st.rerun()

            st.markdown("---")

            st.subheader("✏️ Edit Candidate")

            conn = sqlite3.connect("secure_voting.db")
            c = conn.cursor()

            c.execute("""
                SELECT id, name
                FROM candidates
                ORDER BY id
            """)

            candidate_list = c.fetchall()
            conn.close()

            if candidate_list:

                candidate_dict = {
                    f"{name} (ID:{cid})": cid
                    for cid, name in candidate_list
                }

                selected = st.selectbox(
                    "Select Candidate",
                    list(candidate_dict.keys())
                )

                candidate_id = candidate_dict[selected]

                conn = sqlite3.connect("secure_voting.db")
                c = conn.cursor()

                c.execute("""
                    SELECT
                    name,
                    party,
                    photo_path
                    FROM candidates
                    WHERE id=?
                """, (candidate_id,))

                old_name, old_party, old_photo = c.fetchone()

                conn.close()

                new_name = st.text_input(
                    "New Candidate Name",
                    value=old_name,
                    key="edit_name"
                )

                new_party = st.text_input(
                    "New Party Name",
                    value=old_party,
                    key="edit_party"
                )

                new_photo = st.file_uploader(
                    "Upload New Photo",
                    type=["jpg", "jpeg", "png"],
                    key="edit_photo"
                )

                if st.button("💾 Update Candidate"):

                    photo_path = old_photo

                    if new_photo is not None:

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

                        with open(photo_path, "wb") as f:
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
                        candidate_id
                    ))

                    conn.commit()
                    conn.close()

                    st.success("✅ Candidate Updated Successfully")

                    st.rerun()

            else:
                st.info("No Candidate Available")
                            

        else:

            st.error("❌ Wrong Admin Password")

        # ─── User list with Delete ──────────────────────────────────────
        st.subheader("📋 All Users")

        conn = sqlite3.connect("secure_voting.db")
        c = conn.cursor()
        c.execute("SELECT username, role, has_voted FROM users ORDER BY role, username")
        users = c.fetchall()
        conn.close()

        # Header row
        h1, h2, h3, h4 = st.columns([3, 2, 2, 1])
        h1.markdown("**👤 Username**")
        h2.markdown("**Role**")
        h3.markdown("**Voted**")                                          
        h4.markdown("**Action**")
        st.markdown("---")

        for uname_u, role_u, voted_u in users:
            voted_label = "✅ Yes" if voted_u else "❌ No"
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            col1.write(f"👤 **{uname_u}**")
            col2.write(role_u)
            col3.write(voted_label)
            with col4:
                if st.button("🗑️", key=f"del_{uname_u}", help=f"Delete {uname_u}"):
                    # Delete face image if exists
                    conn = sqlite3.connect("secure_voting.db")
                    c = conn.cursor()
                    c.execute("SELECT face_img_path FROM users WHERE username=?", (uname_u,))
                    face_row = c.fetchone()
                    conn.close()
                    if face_row and face_row[0] and os.path.exists(face_row[0]):
                        os.remove(face_row[0])
                    # Delete from DB
                    conn = sqlite3.connect("secure_voting.db")
                    c = conn.cursor()
                    c.execute("DELETE FROM users WHERE username=?", (uname_u,))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ **{uname_u}** deleted!")
                    st.rerun()

    else:
        if admin_pass:
            st.error("❌ Wrong Admin Password!")
        st.info("Contact the system administrator for the admin password.")
