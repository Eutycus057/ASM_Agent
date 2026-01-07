import os
import time
import requests
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv
from moviepy import ImageClip, vfx

load_dotenv()

class CinematicVideoGenerator:
    def __init__(self):
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.openai_client = OpenAI(api_key=self.openai_api_key) if self.openai_api_key else None

    def generate_base_image(self, prompt: str, output_path: str, retry_count: int = 0) -> Optional[str]:
        """
        Generates a high-quality base image using DALL-E 3 (via OpenAI).
        Includes a Gemini-powered prompt sanitizer to avoid safety violations.
        """
        if not self.openai_client:
            print("OPENAI_API_KEY not found.")
            return None

        # Sanitize prompt using Gemini if available
        from tools.gemini_director import gemini_director
        clean_prompt = gemini_director.sanitize_visual_prompt(prompt) if retry_count == 0 else prompt

        try:
            print(f"--- Generating Base Image (DALL-E 3) [Attempt {retry_count+1}]: {clean_prompt[:50]}... ---")
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=f"Cinematic wide shot, photorealistic, 8k: {clean_prompt}",
                size="1024x1024",
                quality="hd",
                n=1,
            )
            image_url = response.data[0].url
            
            # Download and save the image
            img_data = requests.get(image_url).content
            with open(output_path, 'wb') as handler:
                handler.write(img_data)
            
            return output_path
        except Exception as e:
            error_msg = str(e).lower()
            if "content_policy_violation" in error_msg and retry_count < 1:
                print("--- DALL-E Safety Violation Detected. Retrying with emergency simplified prompt... ---")
                # Immediate fallback: Remove potentially sensitive verbs
                import re
                safe_prompt = re.sub(r'(blinded|blood|gory|dead|kill|exploding|explosion|violent|destruction|crumbling)', 'dramatic', clean_prompt, flags=re.IGNORECASE)
                return self.generate_base_image(safe_prompt, output_path, retry_count=1)
            
            print(f"Error generating base image: {e}")
            print("--- DALL-E failed. Attempting Gemini Imagen Fallback... ---")
            return self.generate_gemini_image(clean_prompt, output_path)

    def generate_gemini_image(self, prompt: str, output_path: str) -> Optional[str]:
        """
        Fallback image generator using Gemini Imagen-3 (if available).
        """
        import os
        import requests
        import google.generativeai as genai
        
        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return None
            
        try:
            genai.configure(api_key=api_key)
            # Try Imagen 3 Fast
            model = genai.GenerativeModel("imagen-3.0-generate-001")
            result = model.generate_content(prompt)
            # Note: The result handling for Imagen in genai might vary depending on version
            # If it's the newer API that returns bytes
            if hasattr(result, 'images') and result.images:
                result.images[0].save(output_path)
                return output_path
            return None
        except Exception as e:
            print(f"Gemini Imagen Fallback failed: {e}")
            return None

    def generate_video(self, image_path: str, output_path: str, duration: float = 6.0, aspect_ratio: str = "16:9") -> Optional[str]:
        """
        Primary entry point for video generation. 
        Uses the Advanced Cinematic Clip engine (Ken Burns 2.0).
        """
        import random
        try:
            print(f"--- Creating Cinematic Video (Ken Burns 2.0): {image_path} ---")
            clip = ImageClip(image_path).with_duration(duration)
            
            # Randomized motion parameters
            zoom_start = 1.0
            zoom_end = random.choice([1.1, 1.15, 1.2]) # Randomized zoom depth
            
            # Randomized pan directions
            pan_x = random.choice(["left", "right", "center"])
            pan_y = random.choice(["up", "down", "center"])
            
            w, h = clip.size
            if aspect_ratio == "9:16":
                target_ratio = 9/16
            else:
                target_ratio = 16/9
                
            if w/h > target_ratio:
                new_w = h * target_ratio
                clip = clip.cropped(x_center=w/2, y_center=h/2, width=new_w, height=h)
            else:
                new_h = w / target_ratio
                clip = clip.cropped(x_center=w/2, y_center=h/2, width=w, height=new_h)
            
            w, h = clip.size 

            def animate_zoom(t):
                return zoom_start + (zoom_end - zoom_start) * (t / duration)

            clip_animated = clip.with_effects([vfx.Resize(animate_zoom)])
            
            if aspect_ratio == "9:16":
                clip_animated = clip_animated.resized(height=1920) 
                final_clip = clip_animated.cropped(x_center=clip_animated.w/2, y_center=1920/2, width=1080, height=1920)
            else:
                clip_animated = clip_animated.resized(height=1080)
                curr_w = clip_animated.w
                x_center = curr_w / 2
                if pan_x == "left": x_center = 1920 / 2
                elif pan_x == "right": x_center = curr_w - (1920 / 2)
                final_clip = clip_animated.cropped(x_center=x_center, y_center=1080/2, width=1920, height=1080)
            
            final_clip.write_videofile(
                output_path, 
                fps=24, 
                codec="libx264", 
                preset="medium", 
                threads=4,
                ffmpeg_params=["-pix_fmt", "yuv420p", "-r", "24"]
            )
            return output_path

        except Exception as e:
            print(f"Cinematic Animation Error: {e}")
            return None

video_generator = CinematicVideoGenerator()
