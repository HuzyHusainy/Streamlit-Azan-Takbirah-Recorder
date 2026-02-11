"""
🕌 Azan & Takbirah Registration System
Main Application Entry Point
"""

import streamlit as st
from config import *
from utils import *
from admin_panel import show_admin_login, show_admin_panel
from github_admin import show_admin_panel_github
from user_form import show_form, show_review_screen, show_thank_you_screen

# ============= PAGE CONFIG =============
st.set_page_config(page_title="Shehrullah Aurangabad", layout="centered")

# ============= STYLING =============
st.markdown(CSS_STYLES, unsafe_allow_html=True)

# ============= SESSION STATE =============
init_session_state()

# ============= BACKGROUND IMAGE =============
@st.cache_data
def get_background():
    import base64
    import os
    if not os.path.exists("assets/ramadan-bg.jpg"):
        return None
    with open("assets/ramadan-bg.jpg", "rb") as img:
        return base64.b64encode(img.read()).decode()

bg = get_background()
if bg:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{bg}");
            background-size: cover;
            background-position: center;
            background-repeat: repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ============= MAIN CONTENT =============

# Admin Login (in sidebar)
show_admin_login()

# Admin Panel (if logged in)
if st.session_state.admin_ok:
    st.sidebar.divider()
    show_admin_panel_github()

st.divider()
st.title("🕌 Azan & Takbirah Registration")

# Thank You Screen (if submitted)
if st.session_state.submitted:
    show_thank_you_screen()

# Main Form
form_data = show_form()

# Review Screen (if review mode)
if st.session_state.review:
    show_review_screen(form_data)
