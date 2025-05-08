import sqlite3
from datetime import datetime

def init_db():
    """Initialize the SQLite database and create the care_logs table if it doesn't exist."""
    conn = sqlite3.connect('homecare.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS care_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            transcript TEXT NOT NULL,
            summary TEXT NOT NULL,
            txt_path TEXT NOT NULL,
            pdf_path TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def log_care_summary(username, filename, transcript, summary, txt_path, pdf_path):
    """
    Log a new care summary entry to the database.
    
    Args:
        username (str): Name of the caregiver
        filename (str): Original audio filename
        transcript (str): Transcribed text
        summary (str): AI-generated summary
        txt_path (str): Path to saved text file
        pdf_path (str): Path to saved PDF file
    """
    try:
        conn = sqlite3.connect('homecare.db')
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO care_logs 
            (username, original_filename, transcript, summary, txt_path, pdf_path)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, filename, transcript, summary, txt_path, pdf_path))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False 