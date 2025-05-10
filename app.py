import streamlit as st
import os
from datetime import datetime
from transcribe import transcribe_audio
from summarize import summarize_text
from export_pdf import export_to_pdf
from database import init_db, log_care_summary
from email_utils import send_pdf_email
from dotenv import load_dotenv

# Load environment variables (for any non-secret configurations)
load_dotenv()

# Check for required secrets
required_secrets = ["GEMINI_API_KEY"]
missing_secrets = [secret for secret in required_secrets if secret not in st.secrets]

if missing_secrets:
    st.warning(f"""
    ⚠️ Missing required secrets in Streamlit configuration:
    {', '.join(missing_secrets)}
    
    Please add these to your .streamlit/secrets.toml file or configure them in Streamlit Cloud.
    """)

# Set page config
st.set_page_config(
    page_title="HomeCare AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
st.markdown("<h1 style='text-align: center; font-size: 40px; margin-bottom: 0;'>🏥 HomeCare AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px; color: gray; margin-top: 0;'>Secure, AI-powered voice documentation for caregivers</p>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid #F0F2F6;'>", unsafe_allow_html=True)

# Login form
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='background-color: #F8FAFC; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>🔐 Caregiver Login</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Please log in to access the system</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 1px solid #F0F2F6;'>", unsafe_allow_html=True)
        
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
        st.markdown("</div>", unsafe_allow_html=True)
else:
    # Main app interface
    with st.container():
        # Top bar with user info and logout
        col1, col2 = st.columns([3,1])
        with col1:
            st.markdown(f"<h3 style='margin: 0;'>👤 Logged in as: {st.session_state.username}</h3>", unsafe_allow_html=True)
        with col2:
            if st.button("Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.experimental_rerun()
        
        st.markdown("<hr style='border: 1px solid #F0F2F6;'>", unsafe_allow_html=True)
        
        # Main workflow section
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h3 style='margin-bottom: 1rem;'>📤 Upload Voice Memo</h3>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Upload a `.wav` or `.mp3` file", type=["wav", "mp3"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if uploaded_file is not None:
                # Save uploaded file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"audio_uploads/{timestamp}_{uploaded_file.name}"
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Process audio
                with st.spinner("🎙️ Transcribing audio..."):
                    transcript = transcribe_audio(file_path)
                
                with st.spinner("🧠 Generating summary..."):
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
            st.markdown("<h3 style='margin-bottom: 1rem;'>📋 Results</h3>", unsafe_allow_html=True)
            if uploaded_file is not None:
                with st.expander("🗒️ Transcript", expanded=True):
                    st.code(transcript, language='text')
                
                with st.expander("🧾 Summary", expanded=True):
                    st.text_area("AI-Generated Summary:", summary, height=250)
                
                # Download options
                st.markdown("<h3 style='margin: 1rem 0;'>📄 Download Summary</h3>", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    with open(txt_path, "r") as f:
                        st.download_button(
                            "📥 Download TXT",
                            f.read(),
                            file_name=f"{base_filename}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                with col2:
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            "📥 Download PDF",
                            f.read(),
                            file_name=f"{base_filename}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                
                # Email section
                st.markdown("<h3 style='margin: 1rem 0;'>✉️ Email Summary</h3>", unsafe_allow_html=True)
                recipient_email = st.text_input("Send to email address")
                if st.button("📩 Send PDF via Email", use_container_width=True):
                    if recipient_email:
                        try:
                            with st.spinner("📧 Sending email..."):
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
st.markdown("<hr style='border: 1px solid #F0F2F6;'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>© 2024 HomeCare AI. All rights reserved.</p>", unsafe_allow_html=True) 