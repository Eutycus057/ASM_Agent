import os
import json
import re
import google.generativeai as genai
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()

class GeminiDirector:
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None
            print("WARNING: Gemini API Key not found. GeminiDirector features will be limited.")

    def sanitize_visual_prompt(self, prompt: str) -> str:
        """
        Uses Gemini to rewrite a visual prompt to be cinematic, descriptive, 
        and compliant with safety filters (e.g., DALL-E 3).
        """
        if not self.model:
            return prompt

        system_instruction = """
        You are a Cinematic Prompt Engineer specializing in photorealistic image generation.
        Your goal is to rewrite the input prompt to be 'DALL-E 3 Safe' while maintaining its emotional power.
        - Replace graphic violence with 'heroic struggle' or 'intense drama'.
        - Replace gore with 'dramatic lighting' or 'intense atmosphere'.
        - Ensure the prompt is descriptive (camera angles, lighting, textures).
        - Output ONLY the rewritten prompt text.
        """

        try:
            response = self.model.generate_content([
                {"role": "user", "parts": [f"{system_instruction}\n\nOriginal Prompt: {prompt}"]}
            ])
            return response.text.strip()
        except Exception as e:
            print(f"Gemini Sanitization Error: {e}")
            return prompt

    def analyze_social_context(self, context: str) -> Dict:
        """
        High-level strategic analysis of a trend or topic.
        """
        if not self.model:
            return {}

        prompt = f"""
        Act as a VIRAL CONTENT STRATEGIST.
        Analyze the following context for a cinematic documentary-style short video:
        Context: {context}

        Provide:
        1. Psychological Hook (Why would someone stop scrolling?)
        2. Narrative Arc (The 'Story' in 60 seconds)
        3. Visual Motif (A recurring visual element for consistency)
        
        Output valid JSON only.
        """

        try:
            response = self.model.generate_content(prompt)
            # Find JSON in response
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                return json.loads(match.group())
            return {}
        except Exception as e:
            print(f"Gemini Analysis Error: {e}")
            return {}

gemini_director = GeminiDirector()
