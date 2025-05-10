import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

def send_pdf_email(recipient_email, subject, body, pdf_path):
    """
    Send a PDF file via email using Gmail SMTP.
    """
    # Check for required secrets
    required_secrets = ["EMAIL_USERNAME", "EMAIL_PASSWORD", "EMAIL_SMTP_SERVER", "EMAIL_SMTP_PORT"]
    missing_secrets = [secret for secret in required_secrets if secret not in st.secrets]
    
    if missing_secrets:
        st.warning(f"Missing email configuration in Streamlit secrets: {', '.join(missing_secrets)}")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = st.secrets["EMAIL_USERNAME"]
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach PDF
        with open(pdf_path, 'rb') as f:
            pdf = MIMEApplication(f.read(), _subtype='pdf')
            pdf.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_path))
            msg.attach(pdf)
        
        # Connect to SMTP server
        server = smtplib.SMTP(st.secrets["EMAIL_SMTP_SERVER"], st.secrets["EMAIL_SMTP_PORT"])
        server.starttls()
        server.login(st.secrets["EMAIL_USERNAME"], st.secrets["EMAIL_PASSWORD"])
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        st.error(f"Error sending email: {str(e)}")
        return False 