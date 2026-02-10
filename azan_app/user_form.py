# ============= USER FORM FUNCTIONS =============

import streamlit as st
import time
from audio_recorder_streamlit import audio_recorder
from config import *
from utils import *
from datetime import datetime

def show_recording_section(audio_type, title, recorder_key):
    """Display recording section with status messages"""
    st.markdown(f"**🎙️ {title}**")
    
    # Check if we have existing audio
    existing_audio = get_audio(audio_type)
    
    # Determine button text
    if existing_audio:
        button_text = "🔄 Record Again"
    else:
        button_text = "🎙️ Tap to Record"
    
    recorded_audio = audio_recorder(
        button_text,
        key=recorder_key,
        pause_threshold=AUDIO_PAUSE_THRESHOLD,
        sample_rate=AUDIO_SAMPLE_RATE
    )
    
    # Save audio if recorded
    if recorded_audio is not None:
        set_audio(audio_type, recorded_audio)
    
    # Display saved audio
    audio_data = get_audio(audio_type)
    if audio_data:
        st.audio(audio_data, format="audio/wav")
        show_inline_success(f"{audio_type}_audio", f"{title} recorded successfully")
    
    return audio_data


def show_form():
    """Display main user registration form"""
    st.subheader("📝 Your Information")

    # NAME FIELD
    name = st.text_input(
        "Aapnu Full Name *",
        placeholder="Enter your full name",
        key="input_name"
    )

    name_valid = False
    if name:
        name_valid, name_error = validate_field(
            "Name",
            name,
            VALIDATION_RULES["name"]
        )
        if name_valid:
            show_inline_success("name", "Valid name")
        else:
            show_inline_error("name", name_error)
    elif st.session_state.validation_errors.get('name'):
        show_inline_error("name", st.session_state.validation_errors['name'])

    # ITS FIELD
    its = st.text_input(
        "ITS Number *",
        placeholder="8 digits only",
        key="input_its",
        max_chars=8
    )

    its_valid = False
    if its:
        existing_its = load_existing_its()
        its_valid, its_error = validate_field(
            "ITS",
            its,
            {
                'pattern': VALIDATION_RULES["its"]["pattern"],
                'custom_check': lambda x: (
                    False, "ITS already registered"
                ) if x in existing_its else (True, None)
            }
        )
        if its_valid:
            show_inline_success("its", "Valid & unique")
        else:
            show_inline_error("its", its_error)
    elif st.session_state.validation_errors.get('its'):
        show_inline_error("its", st.session_state.validation_errors['its'])

    # WHATSAPP FIELD
    whatsapp = st.text_input(
        "WhatsApp Number *",
        placeholder="9876543210",
        key="input_whatsapp",
        max_chars=15
    )

    whatsapp_valid = False
    if whatsapp:
        whatsapp_valid, whatsapp_error = validate_field(
            "WhatsApp",
            whatsapp,
            VALIDATION_RULES["whatsapp"]
        )
        if whatsapp_valid:
            show_inline_success("whatsapp", "Valid format")
        else:
            show_inline_error("whatsapp", whatsapp_error)
    elif st.session_state.validation_errors.get('whatsapp'):
        show_inline_error("whatsapp", st.session_state.validation_errors['whatsapp'])

    # MASJID FIELD
    masjid = st.selectbox(
        "Shehrullah 1447 ma Kai Masjid ma Namaz ada karso? *",
        MASJID_LIST,
        key="select_masjid"
    )

    if not masjid and st.session_state.validation_errors.get('masjid'):
        show_inline_error("masjid", st.session_state.validation_errors['masjid'])
    elif masjid:
        show_inline_success("masjid", f"Selected: {masjid}")

    # INTERESTS
    st.subheader("🎙️ Recording Preferences")

    interest_azan = st.checkbox("Record Azan", key="checkbox_azan")
    interest_takbirah = st.checkbox("Record Takbirah", key="checkbox_takbirah")

    if not (interest_azan or interest_takbirah) and st.session_state.validation_errors.get('interests'):
        show_inline_error("interests", st.session_state.validation_errors['interests'])

    # RECORDINGS - Get audio data from session state
    azan_audio = get_audio("azan") if interest_azan else None
    takbirah_audio = get_audio("takbirah") if interest_takbirah else None

    if interest_azan:
        azan_audio = show_recording_section("azan", "Azan Recording", "azan_recorder")

    if interest_takbirah:
        takbirah_audio = show_recording_section("takbirah", "Takbirah Recording", "takbirah_recorder")

    # REMARKS
    st.subheader("📝 Additional Information")
    remarks = st.text_area(
        "Remarks / Requests (Optional)",
        placeholder="Any additional information you'd like to share",
        key="textarea_remarks"
    )

    # VALIDATION
    errors = {}
    existing_its = load_existing_its()

    if not name:
        errors['name'] = "Name is required"
    elif not name_valid:
        errors['name'] = "Name must be 6–60 characters"

    if not its:
        errors['its'] = "ITS is required"
    elif not its.isdigit() or len(its) != 8:
        errors['its'] = "ITS must be 8 digits"
    elif its in existing_its:
        errors['its'] = "ITS already registered"

    if not whatsapp:
        errors['whatsapp'] = "WhatsApp number is required"
    elif not whatsapp_valid:
        errors['whatsapp'] = "Invalid WhatsApp number (7-15 digits)"

    if not masjid:
        errors['masjid'] = "Masjid selection is required"

    if not (interest_azan or interest_takbirah):
        errors['interests'] = "Select at least one recording interest"

    if interest_azan and not azan_audio:
        errors['azan_audio'] = "Azan recording is required"

    if interest_takbirah and not takbirah_audio:
        errors['takbirah_audio'] = "Takbirah recording is required"

    st.session_state.validation_errors = errors

    # REVIEW BUTTON
    col_review, col_space = st.columns([1, 1])

    with col_review:
        if st.button(
            "🔍 Review Answers",
            use_container_width=True,
            key="btn_review"
        ):
            if errors:
                st.toast("⚠️ Please fix errors above before reviewing", icon="⚠️")
                time.sleep(0.5)
                st.rerun()
            else:
                st.session_state.review = True
                st.rerun()

    return {
        'name': name,
        'its': its,
        'whatsapp': whatsapp,
        'masjid': masjid,
        'interests': (interest_azan, interest_takbirah),
        'azan_audio': azan_audio,
        'takbirah_audio': takbirah_audio,
        'remarks': remarks,
    }


def show_review_screen(form_data):
    """Display review/confirmation screen"""
    st.subheader("✅ Review Your Submission")

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Name:**", form_data['name'])
        st.write("**ITS:**", form_data['its'])
    with col2:
        st.write("**WhatsApp:**", form_data['whatsapp'])
        st.write("**Masjid:**", form_data['masjid'])

    st.write("**Remarks:**", form_data['remarks'] or "No comments")

    interest_azan, interest_takbirah = form_data['interests']
    
    if interest_azan:
        st.write("**Azan Recording:**")
        st.audio(form_data['azan_audio'], format="audio/wav")
    
    if interest_takbirah:
        st.write("**Takbirah Recording:**")
        st.audio(form_data['takbirah_audio'], format="audio/wav")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✏️ Edit", use_container_width=True, key="btn_edit"):
            st.session_state.review = False
            st.rerun()

    with col2:
        if st.button(
            "✅ Submit",
            use_container_width=True,
            key="btn_submit",
            type="primary",
            disabled=st.session_state.submit_clicked
        ):
            if not st.session_state.submit_clicked:
                st.session_state.submit_clicked = True
                
                interest_azan, interest_takbirah = form_data['interests']
                row = {
                    "name": form_data['name'],
                    "its": form_data['its'],
                    "whatsapp": form_data['whatsapp'],
                    "masjid": form_data['masjid'],
                    "interests": ", ".join(
                        i for i, v in {
                            "Azan": interest_azan,
                            "Takbirah": interest_takbirah
                        }.items() if v
                    ),
                    "azan_file": save_audio(form_data['azan_audio'], "azan", form_data['its']) if interest_azan else "",
                    "takbirah_file": save_audio(form_data['takbirah_audio'], "takbirah", form_data['its']) if interest_takbirah else "",
                    "remarks": form_data['remarks'] if form_data['remarks'] else "No comments",  # ← Fix for NaN
                    "submitted_at": datetime.now().isoformat()
                }

                if save_submission(row):
                    st.session_state.submitted = True
                    st.session_state.review = False
                    st.session_state.submit_clicked = False
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.session_state.submit_clicked = False


def show_thank_you_screen():
    """Display thank you screen after submission"""
    st.success("🎉 Thank you! Your response has been recorded.")

    st.markdown(
        """
        **Jazakallah Khair** for your interest in Azan & Takbirah.
        """
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Submit another response", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key != "admin_ok":
                    del st.session_state[key]
            st.rerun()

    with col2:
        st.markdown("🙏 Shukran Jazeelan.")

    st.stop()
