import os
import asyncio
import edge_tts
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv
import re

def clean_narration_text(text: str) -> str:
    """
    Removes scene labels, timestamps, and metadata from narration text
    before sending it to TTS.
    """
    # Remove scene headers like "Scene 1:", "SCENE 2"
    text = re.sub(r"scene\s*\d+\s*:?", "", text, flags=re.IGNORECASE)

    # Remove timestamps like (0–30s), (00:00–00:30), [30s–60s]
    text = re.sub(r"\(.*?\)|\[.*?\]", "", text)

    # Remove extra blank lines
    text = re.sub(r"\n{2,}", "\n", text)

    return text.strip()

load_dotenv()

class AudioGenerator:
    def __init__(self, output_dir: str = "frontend/assets"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    async def generate_speech_async(self, text: str, filename: str) -> Optional[str]:
        """
        Converts text to speech using ElevenLabs as primary, 
        OpenAI TTS as secondary, and edge-tts as final fallback.
        """
        output_path = os.path.join(self.output_dir, filename)
        text = clean_narration_text(text)
        
        elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
        
        # 1. Try ElevenLabs (Premium)
        if elevenlabs_key:
            try:
                print(f"--- Generating Premium Speech (ElevenLabs): {filename} ---")
                import requests
                # Default "Adam" voice ID
                voice_id = "pNInz6obpgDQGcFmaJgB" 
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
                
                headers = {
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": elevenlabs_key
                }
                
                data = {
                    "text": text,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75
                    }
                }
                
                response = requests.post(url, json=data, headers=headers)
                if response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    return output_path
                else:
                    print(f"ElevenLabs API Error ({response.status_code}): {response.text}")
            except Exception as e:
                print(f"ElevenLabs Error, falling back: {e}")

        # 2. Try OpenAI TTS (Standard)
        if self.api_key and self.client:
            try:
                print(f"--- Generating Speech (OpenAI TTS): {filename} ---")
                response = self.client.audio.speech.create(
                    model="tts-1",
                    voice="onyx",
                    input=text
                )
                response.stream_to_file(output_path)
                return output_path
            except Exception as e:
                print(f"OpenAI TTS Error, falling back to Edge TTS: {e}")

        # Fallback to Edge TTS
        try:
            print(f"--- Generating Speech (Edge TTS Fallback): {filename} ---")
            communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural")
            await communicate.save(output_path)
            return output_path
        except Exception as e:
            print(f"Audio Generation Error: {e}")
            return None

audio_generator = AudioGenerator()
