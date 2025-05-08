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

# Set page config with custom theme
st.set_page_config(
    page_title="HomeCare AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        background-color: #4B8BBE;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #306998;
    }
    .header-text {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .subheader-text {
        font-size: 1.2rem;
        color: #64748B;
        margin-bottom: 2rem;
    }
    .login-box {
        background-color: #F8FAFC;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 1rem;
        background-color: #F8FAFC;
        color: #64748B;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize database
init_db()

# Ensure required directories exist
os.makedirs("audio_uploads", exist_ok=True)
os.makedirs("summaries", exist_ok=True)

# Login system
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Predefined users
USERS = {
    "caregiver1": "password123",
    "admin": "adminpass"
}

# Main app header
st.markdown('<div class="header-text">🏥 HomeCare AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader-text">Secure, AI-powered care documentation for caregivers</div>', unsafe_allow_html=True)

# Login form
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("### 🔐 Caregiver Login")
        st.markdown("Please log in to access the system")
        st.markdown("---")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", use_container_width=True):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")
                st.stop()
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # Main app interface
    # Top bar with user info and logout
    col1, col2 = st.columns([3,1])
    with col1:
        st.markdown(f"### 👤 Logged in as: {st.session_state.username}")
    with col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.experimental_rerun()
    
    st.markdown("---")
    
    # Main workflow section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📝 New Voice Log")
        uploaded_file = st.file_uploader("Upload Voice Memo", type=["wav", "mp3"])
        
        if uploaded_file is not None:
            # Save uploaded file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"audio_uploads/{timestamp}_{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Process audio
            with st.spinner("Transcribing audio..."):
                transcript = transcribe_audio(file_path)
            
            with st.spinner("Generating summary..."):
                summary = summarize_text(transcript)
            
            # Save files
            base_filename = f"care_log_{timestamp}"
            txt_path = f"summaries/{base_filename}.txt"
            pdf_path = f"summaries/{base_filename}.pdf"
            
            with open(txt_path, "w") as f:
                f.write(summary)
            
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
                st.success("✅ Log saved successfully!")
            else:
                st.error("❌ Error saving to database")
    
    with col2:
        st.markdown("### 📋 Results")
        if uploaded_file is not None:
            with st.expander("📄 Transcript", expanded=True):
                st.text_area("", transcript, height=200)
            
            with st.expander("🤖 AI Summary", expanded=True):
                st.text_area("", summary, height=200)
            
            # Download options
            st.markdown("### 💾 Download Options")
            col1, col2 = st.columns(2)
            with col1:
                with open(txt_path, "r") as f:
                    st.download_button(
                        "📥 Download Text",
                        f.read(),
                        file_name=f"{base_filename}.txt",
                        mime="text/plain"
                    )
            with col2:
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "📥 Download PDF",
                        f.read(),
                        file_name=f"{base_filename}.pdf",
                        mime="application/pdf"
                    )
            
            # Email section
            st.markdown("### ✉️ Email Summary")
            recipient_email = st.text_input("Send to email address")
            if st.button("Send Email", use_container_width=True):
                if recipient_email:
                    try:
                        if send_pdf_email(
                            recipient_email,
                            f"Care Log Summary - {base_filename}",
                            f"Please find attached the care log summary for {uploaded_file.name}.",
                            pdf_path
                        ):
                            st.success("✅ Email sent successfully!")
                        else:
                            st.error("❌ Failed to send email")
                    except ValueError as e:
                        st.error(f"❌ {str(e)}")
                else:
                    st.warning("⚠️ Please enter a recipient email address")

# Footer
st.markdown("---")
st.markdown('<div class="footer">© 2024 HomeCare AI. All rights reserved.</div>', unsafe_allow_html=True) 