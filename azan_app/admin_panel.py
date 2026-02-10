# ============= ADMIN PANEL FUNCTIONS =============

import streamlit as st
import pandas as pd
import os
import time
from config import *
from utils import *

def show_admin_login():
    """Display admin login in sidebar"""
    with st.sidebar:
        if os.path.exists("assets/umoor.png"):
            st.image("assets/umoor.png", width=180)
        
        st.subheader("🔐 Admin Login")
        
        if not st.session_state.admin_ok:
            pwd = st.text_input("Password", type="password", key="admin_pwd")
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin_ok = True
                st.success("✓ Admin access granted")
        else:
            st.success("✓ Logged in")


def show_admin_panel():
    """Display main admin panel"""
    if not st.session_state.admin_ok:
        return
    
    st.sidebar.divider()
    st.sidebar.subheader("📊 Admin Panel")

    if not os.path.exists(DATA_FILE):
        st.sidebar.info("No submissions yet")
        return

    try:
        df = pd.read_csv(DATA_FILE)
        st.sidebar.write(f"Total Submissions: **{len(df)}**")

        st.sidebar.subheader("🔍 Filter & Review")

        masjid = st.sidebar.selectbox(
            "Filter by Masjid",
            ["All"] + sorted(df["masjid"].dropna().unique().tolist()),
            key="filter_masjid"
        )
        
        display_df = df if masjid == "All" else df[df["masjid"] == masjid]
        
        # Show assessment statistics at top
        st.subheader("📊 Assessment Summary")
        
        # Calculate assessment statistics - get unique ITS only
        assessed = 0
        if os.path.exists(REVIEW_FILE):
            review_df = pd.read_csv(REVIEW_FILE)
            review_df["its"] = review_df["its"].astype(str)
            display_df_its = display_df["its"].astype(str)
            # Get UNIQUE ITS that have been reviewed (in case of duplicate reviews)
            reviewed_unique = review_df[review_df["its"].isin(display_df_its)]["its"].unique()
            assessed = len(reviewed_unique)
        
        pending = len(display_df) - assessed
        
        # Show metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Submissions", len(display_df))
        with col2:
            st.metric("Assessed", assessed, delta=None)
        with col3:
            st.metric("Pending", max(0, pending), delta=None)  # Ensure pending is not negative
        
        # Show masjid-wise assessment chart (always, if multiple masjids exist)
        all_masjids = df["masjid"].dropna().unique()
        if len(all_masjids) > 1:
            st.write("**Assessment Status by Masjid**")
            
            masjid_stats = []
            for m in all_masjids:
                masjid_df = df[df["masjid"] == m]
                if os.path.exists(REVIEW_FILE):
                    reviewed_its = review_df[review_df["its"].isin(masjid_df["its"].astype(str))]["its"].unique()
                    assessed_m = len(reviewed_its)
                else:
                    assessed_m = 0
                pending_m = len(masjid_df) - assessed_m
                
                masjid_stats.append({
                    "Masjid": m,
                    "Assessed": assessed_m,
                    "Pending": pending_m
                })
            
            if masjid_stats:
                stats_df = pd.DataFrame(masjid_stats)
                stats_df = stats_df.set_index("Masjid")
                
                # Use Streamlit bar chart
                st.bar_chart(stats_df, color=('green','yellow'),horizontal=True)
        
        st.divider()

        selected_its = st.sidebar.selectbox(
            "Select Submission (ITS)",
            display_df["its"].astype(str).tolist(),
            key="select_its"
        )
        
        if not selected_its:
            st.info("Select an ITS to review")
            return

        # Always load existing review for the selected ITS
        existing_review = load_existing_review(selected_its)
        
        # Update session state with loaded review
        if existing_review:
            st.session_state.review_status = existing_review["status"]
            st.session_state.review_comment = existing_review["admin_comment"]
        else:
            st.session_state.review_status = ""
            st.session_state.review_comment = ""
        
        # Store current ITS for change detection
        st.session_state.selected_its_prev = selected_its

        row = display_df[display_df["its"].astype(str) == selected_its].iloc[0]

        st.subheader("🎧 Submission Assessment")
        
        # Display submission details in columns
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Name:**", row["name"])
            st.write("**ITS:**", row["its"])
            st.write("**WhatsApp:**", row["whatsapp"])
        with col2:
            st.write("**Masjid:**", row["masjid"])
            st.write("**Interests:**", row["interests"])
            st.write("**Submitted:**", row["submitted_at"][:10])
        
        if row["remarks"]:
            st.info(f"**Remarks:** {row['remarks']}")

        # Display audio files
        st.write("**Audio Recordings:**")
        col_azan, col_takbirah = st.columns(2)
        
        with col_azan:
            if isinstance(row["azan_file"], str) and os.path.exists(row["azan_file"]):
                st.write("🎙️ Azan")
                with open(row["azan_file"], "rb") as f:
                    st.audio(f.read(), format="audio/wav")
            else:
                st.caption("No Azan recording")
        
        with col_takbirah:
            if isinstance(row["takbirah_file"], str) and os.path.exists(row["takbirah_file"]):
                st.write("🎙️ Takbirah")
                with open(row["takbirah_file"], "rb") as f:
                    st.audio(f.read(), format="audio/wav")
            else:
                st.caption("No Takbirah recording")
        
        st.divider()
        
        # Check if review already exists
        existing_review = load_existing_review(selected_its)
        
        if existing_review:
            # Show existing review status
            status_map = {
                "Approved": "review-badge-approved",
                "Needs Improvement": "review-badge-improvement",
                "Not Okay": "review-badge-not-okay"
            }
            badge_class = status_map.get(existing_review["status"], "review-badge-approved")
            
            st.markdown(f"""
                <div style="background-color: #f5f5f5; padding: 1rem; border-radius: 8px;">
                <p><b>Last Review:</b> {existing_review['reviewed_at'][:10]}</p>
                <div class="review-badge {badge_class}">
                    {existing_review['status']}
                </div>
                <p><b>Comments:</b> {existing_review['admin_comment']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("**Update Review:**")
        else:
            st.write("**Create New Review:**")
        
        # Review form
        review_status_options = ["Approved", "Needs Improvement", "Not Okay"]
        current_index = (
            review_status_options.index(st.session_state.review_status)
            if st.session_state.review_status in review_status_options else 0
        )
        
        review_status = st.radio(
            "Decision",
            review_status_options,
            index=current_index,
            key="review_status_radio",
            horizontal=True
        )
        st.session_state.review_status = review_status
        
        review_comment = st.text_area(
            "Admin Comments (Optional)",
            value=st.session_state.review_comment,
            placeholder="Provide feedback for the applicant...",
            key="review_comment_area",
            height=120
        )
        st.session_state.review_comment = review_comment

        col_save, col_notes = st.columns([3, 1])
        
        with col_save:
            if st.button(
                "💾 Save Review",
                key="save_review_btn",
                use_container_width=True,
                type="primary"
            ):
                upsert_admin_review(
                    its=selected_its,
                    status=st.session_state.review_status,
                    comment=st.session_state.review_comment
                )
                st.success("✓ Review saved successfully")
                st.balloons()
                time.sleep(1)
                st.rerun()
        
        with col_notes:
            st.caption(f"ITS: {selected_its}")

    except Exception as e:
        st.sidebar.error(f"Error loading submissions: {e}")