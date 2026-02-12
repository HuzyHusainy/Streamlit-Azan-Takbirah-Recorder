# ============= GLOBAL CONFIGURATION =============
import streamlit as st

# Admin
ADMIN_PASSWORD = "azan"
# ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]

# Files & Directories
DATA_FILE = "submissions.csv"
UPLOAD_DIR = "uploads"
REVIEW_FILE = "admin_reviews.csv"

# Audio Settings
AUDIO_PAUSE_THRESHOLD = 6.0  # seconds
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

# CSS Styles - Mobile Optimized & Dark Mode Compatible
CSS_STYLES = """
<style>
/* ========== BASE STYLES ========== */
.block-container {
    background-color: rgba(255, 255, 255, 0.92);
    padding: 2rem;
    border-radius: 12px;
    max-width: 900px;
}

/* ========== TEXT & LABELS (Desktop) ========== */
label {
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    color: #333 !important;
    display: block !important;
}

.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: #1a1a1a;
}

.stCaption {
    font-size: 0.9rem;
    color: #555;
}

/* ========== DARK MODE ========== */
[data-theme="dark"] label {
    color: #e0e0e0 !important;
}

[data-theme="dark"] .stMarkdown h1,
[data-theme="dark"] .stMarkdown h2,
[data-theme="dark"] .stMarkdown h3 {
    color: #e0e0e0;
}

[data-theme="dark"] .stCaption {
    color: #b0b0b0;
}

/* ========== VALIDATION STYLES ========== */
.validation-error {
    color: #d32f2f;
    font-weight: 500;
    margin-top: 0.25rem;
    font-size: 0.85rem;
}

.validation-success {
    color: #2e7d32;
    font-weight: 500;
    margin-top: 0.25rem;
    font-size: 0.85rem;
}

/* ========== REVIEW BADGE STYLES ========== */
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

/* ========== LOADING SPINNER ========== */
.stSpinner {
    color: #4CAF50 !important;
}

/* ========== MOBILE RESPONSIVE (max-width: 640px) ========== */
@media (max-width: 640px) {
    /* Much larger labels on mobile */
    label {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        line-height: 1.6 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Larger section headers */
    .stMarkdown h1 {
        font-size: 1.8rem !important;
        margin-top: 1.5rem !important;
    }
    
    .stMarkdown h2 {
        font-size: 1.4rem !important;
        margin-top: 1.2rem !important;
    }
    
    .stMarkdown h3 {
        font-size: 1.2rem !important;
    }
    
    /* Larger buttons on mobile */
    .stButton button {
        font-size: 1.1rem !important;
        padding: 0.8rem !important;
        min-height: 50px !important;
        width: 100% !important;
    }
    
    /* Larger input fields */
    .stSelectbox input, .stTextInput input, .stTextArea textarea {
        font-size: 1.1rem !important;
    }
    
    /* Larger checkboxes */
    .stCheckbox label {
        font-size: 1.15rem !important;
        padding: 0.5rem !important;
    }
    
    /* Better spacing */
    .stForm {
        padding: 1rem !important;
    }
    
    /* Reduce padding to save space */
    .block-container {
        padding: 1rem !important;
    }
    
    /* Audio player larger on mobile */
    audio {
        width: 100% !important;
        min-height: 50px !important;
    }
}

/* ========== DESKTOP (min-width: 641px) ========== */
@media (min-width: 641px) {
    .stMarkdown h1 {
        font-size: 2.1rem;
    }
    
    .stMarkdown h2 {
        font-size: 1.6rem;
    }
    
    .stMarkdown h3 {
        font-size: 1.25rem;
    }
}

/* ========== BATTERY SAVER / REDUCED MOTION ========== */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* ========== PERFORMANCE OPTIMIZATION ========== */
/* Reduce repaints with will-change */
.stButton, .stSelectbox, input, textarea {
    will-change: auto;
}

</style>
"""