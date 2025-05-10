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
required_secrets = ["GEMINI_API_KEY", "EMAIL_USERNAME", "EMAIL_PASSWORD"]
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

# Custom CSS for the login page
st.markdown("""
    <style>
    /* Main container */
    .main {
        padding: 0;
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
    }
    
    /* Login container */
    .login-container {
        display: flex;
        min-height: 100vh;
        background: white;
        box-shadow: 0 0 20px rgba(0,0,0,0.1);
    }
    
    /* Left column */
    .login-left {
        background: linear-gradient(135deg, #4B9CD3 0%, #2C5282 100%);
        padding: 4rem 2rem;
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }
    
    /* Right column */
    .login-right {
        padding: 4rem 2rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* Typography */
    .login-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: white;
    }
    
    .login-subtitle {
        font-size: 1.2rem;
        color: rgba(255,255,255,0.9);
        margin-bottom: 2rem;
    }
    
    .login-form-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2C5282;
        margin-bottom: 2rem;
    }
    
    /* Form elements */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        padding: 0.75rem;
        font-size: 1rem;
    }
    
    .stButton > button {
        background-color: #4B9CD3;
        color: white;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        border: none;
        width: 100%;
        transition: background-color 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #2C5282;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .login-container {
            flex-direction: column;
        }
        .login-left, .login-right {
            padding: 2rem 1rem;
        }
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
st.markdown("<h1 style='text-align: center; font-size: 40px; margin-bottom: 0;'>🏥 HomeCare AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px; color: gray; margin-top: 0;'>Secure, AI-powered voice documentation for caregivers</p>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid #F0F2F6;'>", unsafe_allow_html=True)

# Login form
if not st.session_state.logged_in:
    st.markdown("""
        <div class="login-container">
            <div class="login-left" style="flex: 0.6;">
                <h1 class="login-title">🏥 HomeCare AI</h1>
                <p class="login-subtitle">Secure, AI-powered voice documentation for caregivers</p>
                <div style="margin-top: 2rem; text-align: left; max-width: 400px;">
                    <h3 style="color: white; margin-bottom: 1rem;">Why HomeCare AI?</h3>
                    <ul style="color: rgba(255,255,255,0.9); list-style-type: none; padding: 0;">
                        <li style="margin-bottom: 0.5rem;">✓ Save time with voice-to-text</li>
                        <li style="margin-bottom: 0.5rem;">✓ Professional documentation</li>
                        <li style="margin-bottom: 0.5rem;">✓ Secure and private</li>
                        <li style="margin-bottom: 0.5rem;">✓ Easy to use</li>
                    </ul>
                </div>
            </div>
            <div class="login-right" style="flex: 0.4;">
                <h2 class="login-form-title">Welcome Back</h2>
                <p style="color: #64748B; margin-bottom: 2rem;">Please log in to access your care documentation.</p>
            """, unsafe_allow_html=True)
    
    # Login form in the right column
    with st.container():
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", type="password", key="password")
        
        if st.button("Log In", use_container_width=True):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")
                st.stop()
    
    st.markdown("</div></div>", unsafe_allow_html=True)
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
            
            # Add supported formats info
            st.markdown("""
            ℹ️ **Supported Audio Formats:**
            - `.wav` - Standard audio format
            - `.mp3` - Compressed audio format
            - `.m4a` - Common mobile recording format
            
            ⚠️ **Not Supported:**
            - Video files (`.mov`, `.mp4`)
            - iOS voice memos (`.m4a` from older iOS versions)
            - Corrupted or empty files
            """)
            
            uploaded_file = st.file_uploader("Upload a voice memo", type=["wav", "mp3", "m4a"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if uploaded_file is not None:
                try:
                    # Save uploaded file with proper extension
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
                    file_path = f"audio_uploads/{timestamp}{file_extension}"
                    
                    # Ensure the uploads directory exists
                    os.makedirs("audio_uploads", exist_ok=True)
                    
                    # Save the file
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Process audio
                    with st.spinner("🎙️ Transcribing audio..."):
                        transcript = transcribe_audio(file_path)
                        if transcript is None:
                            st.error("❌ Could not transcribe the audio file. Please try a different file.")
                            st.stop()
                    
                    with st.spinner("🧠 Generating summary..."):
                        summary = summarize_text(transcript)
                    
                    # Save files
                    base_filename = f"care_log_{timestamp}"
                    txt_path = f"summaries/{base_filename}.txt"
                    pdf_path = f"summaries/{base_filename}.pdf"
                    
                    # Ensure the summaries directory exists
                    os.makedirs("summaries", exist_ok=True)
                    
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
                    
                except Exception as e:
                    st.error(f"❌ Error processing file: {str(e)}")
                    st.stop()
        
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
st.markdown("<p style='text-align: center; color: gray;'>© 2025 HomeCare AI. All rights reserved.</p>", unsafe_allow_html=True) 