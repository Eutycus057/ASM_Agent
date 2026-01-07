import os
import time
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class MusicGenerator:
    def __init__(self):
        self.api_key = os.environ.get("ELEVENLABS_API_KEY")
        self.local_music_dir = "local_assets/music"
        if not os.path.exists(self.local_music_dir):
            os.makedirs(self.local_music_dir, exist_ok=True)

    def generate_background_music(self, prompt: str, output_path: str, duration: int = 60) -> Optional[str]:
        """
        Generates a background music track using ElevenLabs Sound Effects/Music.
        If API fails or credits are exhausted, falls back to a local royalty-free library.
        """
        if not self.api_key:
            print("ELEVENLABS_API_KEY for Music Generation not found. Using local fallback.")
            return self.get_local_music_fallback(output_path)

        try:
            print(f"--- Generating Background Music (ElevenLabs): {prompt} ({duration}s) ---")
            
            # Note: ElevenLabs has a Sound Effects API that can generate music-like clips. 
            # For specific "Music API", we use the sound-generation endpoint with a high duration if supported, 
            # or the dedicated music model if available.
            url = "https://api.elevenlabs.io/v1/sound-generation"
            
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "text": f"Background music: {prompt}",
                "duration_seconds": min(duration, 22), # Sound effects API max is usually lower, but let's try
                "prompt_influence": 0.3
            }
            
            response = requests.post(url, json=data, headers=headers)

            # Fallback to local music if credits are low or API fails
            if response.status_code != 200:
                print(f"ELEVENLABS_MUSIC_ISSUE ({response.status_code}): Using fallback from local library.")
                return self.get_local_music_fallback(output_path)

            with open(output_path, "wb") as f:
                f.write(response.content)
            
            print(f"Background music saved to {output_path}")
            return output_path

        except Exception as e:
            print(f"Music Generation Exception: {e}. Falling back to local.")
            return self.get_local_music_fallback(output_path)

    def get_local_music_fallback(self, output_path: str) -> Optional[str]:
        """
        Picks a random track from the local 'YouTube Audio style' library.
        """
        import shutil
        import random
        
        if not os.path.exists(self.local_music_dir):
            return None
            
        tracks = [f for f in os.listdir(self.local_music_dir) if f.endswith(('.mp3', '.wav'))]
        if not tracks:
            print("No local music tracks found in local_assets/music/")
            return None
            
        selected_track = random.choice(tracks)
        source_path = os.path.join(self.local_music_dir, selected_track)
        
        print(f"--- Practical Fallback: Using {selected_track} from local library ---")
        shutil.copy(source_path, output_path)
        return output_path

music_generator = MusicGenerator()
