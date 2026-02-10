# ============= UTILITY FUNCTIONS =============

import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from config import *

# ============= VALIDATION FUNCTIONS =============

def validate_field(field_name, value, rules):
    """
    Validate a single field and return (is_valid, error_message)
    """
    if rules.get('required') and not value:
        return False, f"{field_name} is required"
    
    if not value:
        return True, None
    
    if rules.get('min_length') and len(value) < rules['min_length']:
        return False, f"Minimum {rules['min_length']} characters required"
    
    if rules.get('max_length') and len(value) > rules['max_length']:
        return False, f"Maximum {rules['max_length']} characters allowed"
    
    if rules.get('pattern'):
        if not re.match(rules['pattern'], value):
            return False, "Invalid format"
    
    if rules.get('custom_check'):
        is_valid, msg = rules['custom_check'](value)
        if not is_valid:
            return False, msg
    
    return True, None


def show_inline_error(field_name, error_message):
    """Display inline error message for a field"""
    st.markdown(
        f"""
        <div class="validation-error">
            ❌ {error_message}
        </div>
        """,
        unsafe_allow_html=True
    )


def show_inline_success(field_name, success_message):
    """Display inline success message for a field"""
    st.markdown(
        f"""
        <div class="validation-success">
            ✓ {success_message}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============= AUDIO FUNCTIONS =============

def save_audio(audio, prefix, its):
    """Save audio file to disk"""
    if not audio:
        return ""
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = f"{prefix}_{its}_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
        path = os.path.join(UPLOAD_DIR, filename)
        with open(path, "wb") as f:
            f.write(audio)
        return path
    except Exception as e:
        st.error(f"Failed to save audio: {e}")
        return ""


def get_audio(audio_type):
    """Safely get recorded audio from session state"""
    key = f"{audio_type}_audio_recorded"
    return st.session_state.get(key, None)


def set_audio(audio_type, data):
    """Safely set recorded audio in session state"""
    key = f"{audio_type}_audio_recorded"
    st.session_state[key] = data


# ============= TIMER FUNCTIONS =============

# ============= DATA FUNCTIONS =============

def load_existing_its():
    """Load existing ITS numbers from CSV"""
    if not os.path.exists(DATA_FILE):
        return set()
    try:
        df = pd.read_csv(DATA_FILE)
        return set(df["its"].astype(str)) if "its" in df.columns else set()
    except Exception as e:
        st.warning(f"Could not load existing submissions: {e}")
        return set()


def upsert_admin_review(its, status, comment):
    """Save or update admin review with Decision: comment format"""
    try:
        # Format comment as "Decision: comment"
        formatted_comment = f"{status}: {comment}" if comment.strip() else f"{status}: No comments"
        
        new_row = {
            "its": str(its),  # Ensure ITS is string
            "status": status,
            "admin_comment": formatted_comment,  # Save with decision prefix
            "reviewed_at": datetime.now().isoformat()
        }

        if os.path.exists(REVIEW_FILE):
            df = pd.read_csv(REVIEW_FILE)
            # Convert ITS column to string for proper comparison
            df["its"] = df["its"].astype(str)
            mask = (df["its"] == str(its))

            if mask.any():
                # Update existing review
                df.loc[mask, "status"] = status
                df.loc[mask, "admin_comment"] = formatted_comment
                df.loc[mask, "reviewed_at"] = datetime.now().isoformat()
            else:
                # Insert new review
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            df = pd.DataFrame([new_row])

        df.to_csv(REVIEW_FILE, index=False)
    except Exception as e:
        st.error(f"Failed to save review: {e}")


def load_existing_review(its):
    """Load existing admin review"""
    if not os.path.exists(REVIEW_FILE):
        return None

    try:
        df = pd.read_csv(REVIEW_FILE)
        match = df[df["its"] == its]

        if match.empty:
            return None

        match = match.sort_values("reviewed_at", ascending=False)
        return match.iloc[0].to_dict()
    except Exception as e:
        st.warning(f"Could not load review: {e}")
        return None


# ============= SUBMISSION FUNCTIONS =============

def save_submission(row):
    """Save form submission to CSV"""
    try:
        pd.DataFrame([row]).to_csv(
            DATA_FILE,
            mode="a",
            header=not os.path.exists(DATA_FILE),
            index=False
        )
        return True
    except Exception as e:
        st.error(f"Failed to save submission: {e}")
        return False


# ============= SESSION STATE INITIALIZATION =============

def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        "review": False,
        "review_saved": False,
        "submitted": False,
        "admin_ok": False,
        "azan_audio_recorded": None,
        "takbirah_audio_recorded": None,
        "review_status": "",
        "review_comment": "",
        "validation_errors": {},
        "submit_clicked": False,
        "selected_its_prev": None,
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value