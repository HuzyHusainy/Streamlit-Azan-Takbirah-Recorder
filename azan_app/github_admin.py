# github_admin.py - GitHub-based Admin Panel

import streamlit as st
import pandas as pd
import requests
import base64
import io
from datetime import datetime
from config import *
from utils import *
import time

# ============= GITHUB FUNCTIONS =============

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_submissions_from_github():
    """Load submissions CSV from GitHub"""
    try:
        token = st.secrets["github"]["token"]
        repo = st.secrets["github"]["repo"]
        url = f"https://api.github.com/repos/{repo}/contents/submissions.csv"
        headers = {"Authorization": f"token {token}"}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            csv_content = base64.b64decode(response.json()['content']).decode()
            df = pd.read_csv(io.StringIO(csv_content))
            return df, response.json()['sha']  # Return sha for updates
        else:
            return None, None
    
    except Exception as e:
        st.error(f"❌ Error loading submissions: {e}")
        return None, None


def load_reviews_from_github():
    """Load reviews CSV from GitHub (or create if doesn't exist)"""
    try:
        token = st.secrets["github"]["token"]
        repo = st.secrets["github"]["repo"]
        url = f"https://api.github.com/repos/{repo}/contents/reviews.csv"
        headers = {"Authorization": f"token {token}"}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            csv_content = base64.b64decode(response.json()['content']).decode()
            df = pd.read_csv(io.StringIO(csv_content))
            return df, response.json()['sha']
        else:
            # File doesn't exist - return empty dataframe
            return pd.DataFrame(), None
    
    except Exception as e:
        st.error(f"❌ Error loading reviews: {e}")
        return None, None


def save_review_to_github(its_number, status, comments):
    """Save admin review to GitHub"""
    try:
        token = st.secrets["github"]["token"]
        repo = st.secrets["github"]["repo"]
        url = f"https://api.github.com/repos/{repo}/contents/reviews.csv"
        headers = {"Authorization": f"token {token}"}
        
        # Load existing reviews
        reviews_df, sha = load_reviews_from_github()
        
        if reviews_df is None:
            reviews_df = pd.DataFrame()
        
        # Check if ITS already has a review
        if not reviews_df.empty and 'its' in reviews_df.columns:
            mask = reviews_df['its'].astype(str) == str(its_number)
            if mask.any():
                # Update existing review
                reviews_df.loc[mask, 'status'] = status
                reviews_df.loc[mask, 'comments'] = comments
                reviews_df.loc[mask, 'reviewed_at'] = datetime.now().isoformat()
            else:
                # Add new review
                new_review = pd.DataFrame([{
                    'its': its_number,
                    'status': status,
                    'comments': comments,
                    'reviewed_at': datetime.now().isoformat()
                }])
                reviews_df = pd.concat([reviews_df, new_review], ignore_index=True)
        else:
            # Create new reviews DataFrame
            reviews_df = pd.DataFrame([{
                'its': its_number,
                'status': status,
                'comments': comments,
                'reviewed_at': datetime.now().isoformat()
            }])
        
        # Convert to CSV
        csv_string = reviews_df.to_csv(index=False)
        encoded = base64.b64encode(csv_string.encode()).decode()
        
        # Prepare GitHub API request
        data = {
            "message": f"Update review for {its_number} - {status}",
            "content": encoded,
            "branch": "main"
        }
        
        if sha:
            data["sha"] = sha
        
        # Push to GitHub
        response = requests.put(url, json=data, headers=headers)
        
        return response.status_code in [201, 200]
    
    except Exception as e:
        st.error(f"❌ Failed to save review: {e}")
        return False


def get_audio_file_url(file_path):
    """Get GitHub URL for audio file"""
    try:
        token = st.secrets["github"]["token"]
        repo = st.secrets["github"]["repo"]
        url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
        headers = {"Authorization": f"token {token}"}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # Return raw content URL for audio playback
            return f"https://raw.githubusercontent.com/{repo}/main/{file_path}"
        else:
            return None
    
    except Exception as e:
        st.error(f"❌ Error getting audio URL: {e}")
        return None


# ============= ADMIN PANEL FUNCTIONS =============

def show_admin_panel_github():
    """Display admin panel with GitHub data"""
    if not st.session_state.admin_ok:
        return
    
    st.sidebar.divider()
    st.sidebar.subheader("📊 Admin Panel")

    # Load data from GitHub
    df, _ = load_submissions_from_github()
    reviews_df, _ = load_reviews_from_github()
    
    if df is None or len(df) == 0:
        st.sidebar.info("No submissions yet")
        return

    try:
        st.sidebar.write(f"Total Submissions: **{len(df)}**")
        st.sidebar.subheader("🔍 Filter & Review")

        # Filter by masjid
        masjid = st.sidebar.selectbox(
            "Filter by Masjid",
            ["All"] + sorted(df["masjid"].dropna().unique().tolist()),
            key="filter_masjid"
        )
        
        display_df = df if masjid == "All" else df[df["masjid"] == masjid]
        
        # Show assessment statistics
        if masjid == "All":
            st.subheader("📊 Assessment Summary")
        else:
            st.subheader(f"📊 Assessment Summary - {masjid}")
        
        assessed = 0
        if reviews_df is not None and not reviews_df.empty and 'its' in reviews_df.columns:
            reviews_df["its"] = reviews_df["its"].astype(str)
            display_df_its = display_df["its"].astype(str)
            reviewed_unique = reviews_df[reviews_df["its"].isin(display_df_its)]["its"].unique()
            assessed = len(reviewed_unique)
        
        pending = len(display_df) - assessed
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Submissions", len(display_df))
        with col2:
            st.metric("Assessed", assessed)
        with col3:
            st.metric("Pending", max(0, pending))
        
        # Show chart for selected masjid (or all if "All" selected)
        if masjid == "All" and len(display_df) > 1:
            st.write("**Assessment Status by Masjid**")
            
            masjid_stats = []
            for m in display_df:
                masjid_df = df[df["masjid"] == m]
                if reviews_df is not None and not reviews_df.empty:
                    reviewed_its = reviews_df[reviews_df["its"].isin(masjid_df["its"].astype(str))]["its"].unique()
                    assessed_m = len(reviewed_its)
                else:
                    assessed_m = 0
                pending_m = len(masjid_df) - assessed_m
                
                masjid_stats.append({
                    "Masjid": m,
                    "Assessed": assessed_m,
                    "Pending": pending_m
                })
            
            stats_df = pd.DataFrame(masjid_stats)
            stats_df = stats_df.set_index("Masjid")
            
            # Create interactive chart with hover info
            st.bar_chart(stats_df, use_container_width=True)
            
            # Show detailed breakdown below chart
            with st.expander("📊 Detailed Breakdown"):
                for stat in masjid_stats:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**{stat['Masjid']}**")
                    with col2:
                        st.write(f"✅ Assessed: {stat['Assessed']}")
                    with col3:
                        st.write(f"⏳ Pending: {stat['Pending']}")
        
        elif masjid != "All":
            # Show chart for selected masjid only
            st.write(f"**Assessment Status - {masjid}**")
            
            masjid_df = df[df["masjid"] == masjid]
            if reviews_df is not None and not reviews_df.empty:
                reviewed_its = reviews_df[reviews_df["its"].isin(masjid_df["its"].astype(str))]["its"].unique()
                assessed_m = len(reviewed_its)
            else:
                assessed_m = 0
            pending_m = len(masjid_df) - assessed_m
            
            # Create single-row dataframe for chart
            stats_df = pd.DataFrame([{
                "Masjid": masjid,
                "Assessed": assessed_m,
                "Pending": pending_m
            }])
            stats_df = stats_df.set_index("Masjid")
            st.bar_chart(stats_df, use_container_width=True)
            
            # Show summary below chart
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", len(masjid_df))
            with col2:
                st.metric("Assessed", assessed_m)
            with col3:
                st.metric("Pending", pending_m)
        
        st.divider()
        
        # Select submission to review
        selected_its = st.sidebar.selectbox(
            "Select Submission (ITS)",
            display_df["its"].astype(str).tolist(),
            key="select_its"
        )
        
        if not selected_its:
            st.info("Select an ITS to review")
            return

        # Get selected row
        row = display_df[display_df["its"].astype(str) == selected_its].iloc[0]

        st.subheader("🎧 Submission Assessment")
        
        # Display submission details
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Name:**", row["name"])
            st.write("**ITS:**", row["its"])
            st.write("**WhatsApp:**", row["whatsapp"])
        with col2:
            st.write("**Masjid:**", row["masjid"])
            st.write("**Interests:**", row["interests"])
            st.write("**Remarks:**", row["remarks"])
        
        st.divider()
        
        # Display audio files
        st.subheader("🎙️ Recordings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if pd.notna(row.get("azan_file")) and row["azan_file"]:
                st.write("**Azan Recording:**")
                audio_url = get_audio_file_url(row["azan_file"])
                if audio_url:
                    st.audio(audio_url, format="audio/wav")
                else:
                    st.caption("❌ Could not load audio")
            else:
                st.caption("No Azan recording")
        
        with col2:
            if pd.notna(row.get("takbirah_file")) and row["takbirah_file"]:
                st.write("**Takbirah Recording:**")
                audio_url = get_audio_file_url(row["takbirah_file"])
                if audio_url:
                    st.audio(audio_url, format="audio/wav")
                else:
                    st.caption("❌ Could not load audio")
            else:
                st.caption("No Takbirah recording")
        
        st.divider()
        
        # Load existing review (if any)
        existing_review = None
        if reviews_df is not None and not reviews_df.empty:
            mask = reviews_df["its"].astype(str) == str(selected_its)
            if mask.any():
                existing_review = reviews_df[mask].iloc[0]
        
        if existing_review is not None:
            # Show existing review
            st.write("**Previous Review:**")
            st.info(f"Status: {existing_review['status']} | {existing_review['reviewed_at'][:10]}")
            st.write(f"Comments: {existing_review['comments']}")
            st.write("**Update Review:**")
        else:
            st.write("**Add Review:**")
        
        # Review form
        col1, col2 = st.columns(2)
        
        with col1:
            status = st.selectbox(
                "Assessment Status",
                ["Approved", "Needs Improvement", "Not Okay"],
                key="review_status"
            )
        
        with col2:
            comments = st.text_area(
                "Comments",
                placeholder="Your feedback...",
                key="review_comments",
                height=120
            )
        
        # Save review button
        if st.button("💾 Save Review", use_container_width=True, type="primary"):
            if save_review_to_github(selected_its, status, comments):
                st.success("✅ Review saved to GitHub!")
                st.cache_data.clear()  # Clear cache to reload data
                time.sleep(1)
                st.rerun()
            else:
                st.error("Failed to save review")
    
    except Exception as e:
        st.error(f"❌ Error in admin panel: {e}")
