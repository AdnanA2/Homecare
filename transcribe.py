import whisper
import tempfile
import os
import streamlit as st
import subprocess

def transcribe_audio(file_path):
    """
    Transcribe audio file using Whisper with proper FFmpeg preprocessing.
    Supports .wav, .mp3, and .m4a files.
    """
    try:
        # Load Whisper model
        model = whisper.load_model("base")
        
        # Create a temporary .wav file for FFmpeg conversion
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
        
        # Convert audio to 16kHz mono WAV using FFmpeg
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", file_path,
            "-ar", "16000",  # Set sample rate to 16kHz
            "-ac", "1",      # Convert to mono
            "-f", "wav",     # Force WAV format
            "-y",            # Overwrite output file if it exists
            tmp_path
        ]
        
        # Run FFmpeg command
        process = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True
        )
        
        if process.returncode != 0:
            st.error(f"❌ Audio conversion failed: {process.stderr}")
            return None
        
        # Transcribe the converted audio
        result = model.transcribe(tmp_path)
        return result["text"]
        
    except Exception as e:
        st.error(f"❌ Transcription failed: {str(e)}")
        return None
        
    finally:
        # Clean up temporary file
        try:
            os.remove(tmp_path)
        except:
            pass  # Ignore cleanup errors 