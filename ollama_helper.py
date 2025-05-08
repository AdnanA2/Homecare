import requests
import subprocess
import time
import streamlit as st

def ensure_ollama_ready(model_name: str = "llama3"):
    """
    This function is temporarily disabled as we're using Gemini instead of LLaMA.
    """
    return True  # Always return True since we're not using LLaMA
    
    """
    # Original LLaMA implementation (commented out)
    try:
        # Check if Ollama API is reachable
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code != 200:
            st.error("Ollama is not running. Please install Ollama from https://ollama.com")
            return False
        
        # Check if model is available
        models = response.json().get("models", [])
        model_exists = any(model["name"] == model_name for model in models)
        
        if not model_exists:
            st.info(f"Starting {model_name} model...")
            subprocess.Popen(["ollama", "run", model_name])
            time.sleep(5)  # Wait for model to start
            
        return True
        
    except requests.exceptions.ConnectionError:
        st.error("Ollama is not running. Please install Ollama from https://ollama.com")
        return False
    """ 