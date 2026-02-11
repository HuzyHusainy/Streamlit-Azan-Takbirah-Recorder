# ============= GLOBAL CONFIGURATION =============
import streamlit as st

# Admin
# ADMIN_PASSWORD = "azan"
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]

# Files & Directories
DATA_FILE = "submissions.csv"
UPLOAD_DIR = "uploads"
REVIEW_FILE = "admin_reviews.csv"

# Audio Settings
AUDIO_PAUSE_THRESHOLD = 5.0  # seconds
AUDIO_SAMPLE_RATE = 16000

# Validation Rules
VALIDATION_RULES = {
    "name": {
        "required": True,
        "min_length": 6,
        "max_length": 60,
    },
    "its": {
        "required": True,
        "pattern": r"^\d{8}$",
    },
    "whatsapp": {
        "required": True,
        "pattern": r"^\d{7,15}$",
    },
    "masjid": {
        "required": True,
    },
}

# Masjid List
MASJID_LIST = ["", "Najmi Masjid", "Saifee Masjid", "Kalimi Masjid", "Vajihi Masjid"]

# CSS Styles
CSS_STYLES = """
<style>
.block-container {
    background-color: rgba(255, 255, 255, 0.92);
    padding: 2rem;
    border-radius: 12px;
    max-width: 900px;
}

/* Input labels */
label {
    font-size: 1.05rem !important;
    font-weight: 600 !important;
}

/* Section headers */
.stMarkdown h1 {
    font-size: 2.1rem;
}

.stMarkdown h2 {
    font-size: 1.6rem;
}

.stMarkdown h3 {
    font-size: 1.25rem;
}

/* Checkbox / radio text */
.stCheckbox label, .stRadio label {
    font-size: 1rem !important;
}

/* Help text under inputs */
.stCaption {
    font-size: 0.9rem;
    color: #555;
}

/* Inline validation styles */
.validation-error {
    color: #d32f2f;
    font-size: 0.85rem;
    margin-top: 0.25rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.validation-success {
    color: #388e3c;
    font-size: 0.85rem;
    margin-top: 0.25rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Recording timer styling - REMOVED (not needed) */

/* Admin review status badge */
.review-badge {
    display: inline-block;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.9rem;
    margin: 0.5rem 0;
}

.review-badge-approved {
    background-color: #c8e6c9;
    color: #1b5e20;
}

.review-badge-improvement {
    background-color: #fff9c4;
    color: #f57f17;
}

.review-badge-not-okay {
    background-color: #ffcdd2;
    color: #b71c1c;
}

/* Mobile responsiveness */
@media (max-width: 600px) {
    .block-container {
        max-width: 100% !important;
        padding: 1rem !important;
    }
    label {
        font-size: 0.95rem !important;
    }
    .stMarkdown h1 {
        font-size: 1.5rem;
    }
    .stMarkdown h2 {
        font-size: 1.2rem;
    }
    /* Ensure buttons are touch-friendly (44px minimum) */
    .stButton > button {
        width: 100% !important;
        min-height: 44px !important;
        font-size: 1rem !important;
    }
}
</style>
"""