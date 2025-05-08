import whisper

def transcribe_audio(file_path: str) -> str:
    """
    Transcribes an audio file using Whisper's base model.
    
    Args:
        file_path (str): Path to the audio file (.wav or .mp3)
        
    Returns:
        str: Transcribed text
    """
    # Load the base model
    model = whisper.load_model("base")
    
    # Transcribe the audio
    result = model.transcribe(file_path)
    
    return result["text"] 