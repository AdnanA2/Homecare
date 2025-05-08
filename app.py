import streamlit as st
import os
from datetime import datetime
from transcribe import transcribe_audio
from summarize import summarize_text
from export_pdf import export_to_pdf
from ollama_helper import ensure_ollama_ready
from database import init_db, log_care_summary
from email_utils import send_pdf_email
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="HomeCare AI",
    page_icon="🏥",
    layout="wide"
)

# Initialize database
init_db()

# Ensure required directories exist
os.makedirs("audio_uploads", exist_ok=True)
os.makedirs("summaries", exist_ok=True)

# Login system
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Predefined users (in a real app, this would be in a database)
USERS = {
    "caregiver1": "password123",
    "admin": "adminpass"
}

# Login form
if not st.session_state.logged_in:
    st.title("🏥 HomeCare AI Login")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")
            st.stop()
else:
    # Main app interface
    st.title("🏥 HomeCare AI")
    
    # Add logout button
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()
    
    st.markdown(f"""
    Welcome, {st.session_state.username}!  
    This app helps caregivers convert voice memos into professional care logs.
    Upload a voice memo (.wav or .mp3) to get started.
    """)
    
    # File uploader
    uploaded_file = st.file_uploader("Upload Voice Memo", type=["wav", "mp3"])
    
    if uploaded_file is not None:
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"audio_uploads/{timestamp}_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Create two columns for progress
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("Transcribing audio...")
            transcript = transcribe_audio(file_path)
            st.success("Transcription complete!")
            
            st.subheader("Transcript")
            st.text_area("", transcript, height=200)
        
        with col2:
            st.info("Generating care log summary...")
            summary = summarize_text(transcript)
            st.success("Summary complete!")
            
            st.subheader("Care Log Summary")
            st.text_area("", summary, height=200)
        
        # Save summary files
        base_filename = f"care_log_{timestamp}"
        txt_path = f"summaries/{base_filename}.txt"
        pdf_path = f"summaries/{base_filename}.pdf"
        
        # Save as text
        with open(txt_path, "w") as f:
            f.write(summary)
        
        # Save as PDF
        export_to_pdf(summary, base_filename)
        
        # Log to database
        if log_care_summary(
            st.session_state.username,
            uploaded_file.name,
            transcript,
            summary,
            txt_path,
            pdf_path
        ):
            st.success(f"Summary saved as {base_filename}.txt and {base_filename}.pdf in the summaries folder!")
        else:
            st.error("Error saving to database")
        
        # Email functionality
        st.subheader("Email Summary")
        recipient_email = st.text_input("Send summary to email:")
        if st.button("Send Email"):
            if recipient_email:
                try:
                    if send_pdf_email(
                        recipient_email,
                        f"Care Log Summary - {base_filename}",
                        f"Please find attached the care log summary for {uploaded_file.name}.",
                        pdf_path
                    ):
                        st.success("Email sent successfully!")
                    else:
                        st.error("Failed to send email")
                except ValueError as e:
                    st.error(str(e))
            else:
                st.warning("Please enter a recipient email address") 