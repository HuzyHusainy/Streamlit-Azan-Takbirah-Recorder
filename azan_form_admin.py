import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from audio_recorder_streamlit import audio_recorder

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Shehrullah Aurangabad", layout="centered")

ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
DATA_FILE = "submissions.csv"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------- HELPERS ----------------
def load_existing_its():
    if not os.path.exists(DATA_FILE):
        return set()
    try:
        df = pd.read_csv(DATA_FILE)
        return set(df["its"].astype(str)) if "its" in df.columns else set()
    except:
        return set()

def save_audio(audio, prefix, its):
    if not audio:
        return ""
    filename = f"{prefix}_{its}_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(audio)
    return path

def is_valid_whatsapp(num):
    return bool(re.fullmatch(r"\d{7,15}", num))

# ---------------- SESSION STATE ----------------
for key in ["review", "admin_ok", "azan_audio", "takbirah_audio"]:
    st.session_state.setdefault(key, False if key == "review" else None)

# ---------------- ADMIN LOGIN ----------------
with st.sidebar:
    st.subheader("🔐 Admin Login")
    if not st.session_state.admin_ok:
        pwd = st.text_input("Password", type="password")
        if pwd == ADMIN_PASSWORD:
            st.session_state.admin_ok = True
            st.success("Admin access granted")
    else:
        st.success("Logged in")

# ---------------- ADMIN PANEL ----------------
if st.session_state.admin_ok:
    st.sidebar.divider()
    st.sidebar.subheader("📂 Admin Panel")

    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        st.sidebar.write(f"Total Submissions: **{len(df)}**")

        masjid = st.selectbox("Filter by Masjid", ["All"] + sorted(df["masjid"].unique()))
        if masjid != "All":
            df = df[df["masjid"] == masjid]

        selected_its = st.sidebar.selectbox(
            "Review Submission (ITS)",
            df["its"].astype(str).tolist()
        )

        row = df[df["its"].astype(str) == selected_its].iloc[0]

        st.subheader("🎧 Assessment")
        st.write("Name:", row["name"])
        st.write("Masjid:", row["masjid"])
        st.write("Interest:", row["interests"])
        st.write("Waqt:", row["waqt"])
        st.write("Remarks:", row["remarks"])

        for label, col in [("Azan", "azan_file"), ("Takbirah", "takbirah_file")]:
            if isinstance(row[col], str) and os.path.exists(row[col]):
                with open(row[col], "rb") as f:
                    st.audio(f.read(), format="audio/wav")
    else:
        st.sidebar.info("No submissions yet")

st.divider()
st.title("🕌 Azan & Takbirah Registration")

existing_its = load_existing_its()

# ---------------- FORM ----------------
name = st.text_input("Aapnu Full Name *")
its = st.text_input("ITS Number *")
whatsapp = st.text_input("WhatsApp Number *", placeholder="9876543210")

masjid = st.selectbox("Shehrullah 1447 ma Kai Masjid ma Namaz ada karso? *", ["", "Najmi Masjid", "Saifee Masjid", "Kalimi Masjid", "Vajihi Masjid", "Jamali Park"])

interest_azan = st.checkbox("Azan")
interest_takbirah = st.checkbox("Takbirah")

if interest_azan:
    st.markdown("🎙 **Azan Recording**")
    st.session_state.azan_audio = audio_recorder("Start / Stop Recording Azan", key="azan")
    if st.session_state.azan_audio:
        st.audio(st.session_state.azan_audio)

if interest_takbirah:
    st.markdown("🎙 **Takbirah Recording**")
    st.session_state.takbirah_audio = audio_recorder("Start / Stop Recording Takbirah", key="takbirah")
    if st.session_state.takbirah_audio:
        st.audio(st.session_state.takbirah_audio)

waqt = st.multiselect("Aapne kaya Waqt ma Azan/Takbirah aapvu che?", ["Fajr", "Zuhr", "Maghrib"])
remarks = st.text_area("Remarks / Requests")

# ---------------- VALIDATION ----------------
errors = []

if not (6 <= len(name) <= 60):
    errors.append("Name must be 6–60 characters")

if not (its.isdigit() and len(its) == 8):
    errors.append("ITS must be exactly 8 digits")
elif its in existing_its:
    errors.append("ITS already registered")

if not is_valid_whatsapp(whatsapp):
    errors.append("Invalid WhatsApp number")

if not masjid:
    errors.append("Masjid required")

if not (interest_azan or interest_takbirah):
    errors.append("Select at least one interest")

if interest_azan and not st.session_state.azan_audio:
    errors.append("Azan recording required")

if interest_takbirah and not st.session_state.takbirah_audio:
    errors.append("Takbirah recording required")

if not waqt:
    errors.append("Select at least one waqt")

# ---------------- REVIEW STEP ----------------
if not st.session_state.review:
    if st.button("🔍 Review Answers"):
        if errors:
            for e in errors:
                st.error(e)
        else:
            st.session_state.review = True

if st.session_state.review:
    st.subheader("📋 Review Submission")

    st.write("Name:", name)
    st.write("ITS:", its)
    st.write("WhatsApp:", whatsapp)
    st.write("Masjid:", masjid)
    st.write("Waqt:", ", ".join(waqt))
    st.write("Remarks:", remarks or "—")

    if interest_azan:
        st.audio(st.session_state.azan_audio)
    if interest_takbirah:
        st.audio(st.session_state.takbirah_audio)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✏️ Edit"):
            st.session_state.review = False

    with col2:
        if st.button("✅ Submit"):
            row = {
                "name": name,
                "its": its,
                "whatsapp": whatsapp,
                "masjid": masjid,
                "interests": ", ".join(
                    i for i, v in {"Azan": interest_azan, "Takbirah": interest_takbirah}.items() if v
                ),
                "waqt": ", ".join(waqt),
                "azan_file": save_audio(st.session_state.azan_audio, "azan", its),
                "takbirah_file": save_audio(st.session_state.takbirah_audio, "takbirah", its),
                "remarks": remarks,
                "submitted_at": datetime.now().isoformat()
            }

            pd.DataFrame([row]).to_csv(
                DATA_FILE,
                mode="a",
                header=not os.path.exists(DATA_FILE),
                index=False
            )

            st.success("Submission successful 🌙")
            st.stop()
