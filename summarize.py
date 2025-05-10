import streamlit as st
import google.generativeai as genai

def summarize_text(text):
    """
    Summarize the given text using Google's Gemini API.
    """
    if "GEMINI_API_KEY" not in st.secrets:
        st.warning("Missing Gemini API key in Streamlit secrets.")
        return "Error: Gemini API key not configured."
    
    try:
        # Configure Gemini API
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # Initialize the model
        model = genai.GenerativeModel('gemini-pro')
        
        # Create the prompt
        prompt = f"""
        As a healthcare documentation specialist, please summarize the following caregiver's voice memo 
        into a clear, professional care log. Focus on key medical observations, patient status, 
        and any actions taken. Use medical terminology where appropriate but keep it accessible.
        
        Voice Memo Transcript:
        {text}
        
        Please provide a structured summary with these sections:
        1. Patient Status
        2. Key Observations
        3. Actions Taken
        4. Follow-up Notes
        """
        
        # Generate the summary
        response = model.generate_content(prompt)
        
        return response.text
        
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return f"Error: {str(e)}"

# Original LLaMA implementation (commented out for now)
"""
def summarize_text(text: str) -> str:
    # Summarizes text using Ollama's LLaMA 3 model.
    
    Args:
        text (str): Text to summarize
        
    Returns:
        str: Summarized text
    
    prompt = f"Summarize this caregiver voice note into a professional, clear care log: {text}"
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )
    
    if response.status_code == 200:
        return response.json()["response"]
    else:
        raise Exception(f"Error from Ollama API: {response.text}")
""" 