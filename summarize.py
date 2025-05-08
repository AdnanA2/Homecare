import requests
import json

# Gemini API configuration (temporary for testing)
GEMINI_API_KEY = "AIzaSyAxrFQPCbJOxoMhKHfcvvvG--Csk6bxg2s"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

def summarize_text(text: str) -> str:
    """
    Summarizes text using Google's Gemini Pro model (temporary implementation).
    Original LLaMA implementation is commented out below.
    
    Args:
        text (str): Text to summarize
        
    Returns:
        str: Summarized text
    """
    # Prepare the prompt
    prompt = f"Summarize this caregiver voice note into a professional, clear care log:\n\n{text}"
    
    # Prepare the request payload
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    # Set up headers with API key
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }
    
    try:
        # Make the API request
        response = requests.post(
            GEMINI_API_URL,
            headers=headers,
            json=payload
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        # Extract the summary from the response
        summary = response.json()['candidates'][0]['content']['parts'][0]['text']
        return summary
        
    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        raise Exception(f"Failed to generate summary: {str(e)}")
    except (KeyError, IndexError) as e:
        print(f"Error parsing Gemini API response: {e}")
        raise Exception("Failed to parse summary from API response")

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