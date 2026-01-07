import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

load_dotenv()

api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("API Key not found")
else:
    genai.configure(api_key=api_key)
    print(f"Using API Key: {api_key[:4]}...{api_key[-4:]}")
    
    for attempt in range(3):
        try:
            print(f"Attempt {attempt + 1}: Listing models...")
            models = genai.list_models()
            available = []
            for m in models:
                if 'generateContent' in m.supported_generation_methods:
                    available.append(m.name)
            
            if available:
                print("Available models:")
                for name in available:
                    print(name)
                break
            else:
                print("No models found with generateContent support.")
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {e}")
            time.sleep(2)
