import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

def send_pdf_email(recipient_email, subject, body, attachment_path):
    """
    Send an email with a PDF attachment using Gmail SMTP.
    
    Args:
        recipient_email (str): Email address of the recipient
        subject (str): Email subject
        body (str): Email body text
        attachment_path (str): Path to the PDF file to attach
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Email configuration
    sender_email = os.getenv('GMAIL_USER')  # Set this in your environment
    sender_password = os.getenv('GMAIL_APP_PASSWORD')  # Set this in your environment
    
    if not sender_email or not sender_password:
        raise ValueError("Gmail credentials not found in environment variables")
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(body, 'plain'))
        
        # Add attachment
        with open(attachment_path, 'rb') as f:
            pdf = MIMEApplication(f.read(), _subtype='pdf')
            pdf.add_header('Content-Disposition', 'attachment', 
                         filename=os.path.basename(attachment_path))
            msg.attach(pdf)
        
        # Send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
            
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False 