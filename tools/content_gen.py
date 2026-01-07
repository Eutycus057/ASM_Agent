import os
import json
import re
from openai import OpenAI
from models import TrendData, ScriptAnalysis, ContentDraft
from dotenv import load_dotenv

load_dotenv()

class ContentGenerator:
    def __init__(self):
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.gemini_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        
        if self.gemini_key:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.use_gemini = True
        else:
            self.use_gemini = False
            from openai import OpenAI
            self.client = OpenAI(api_key=self.openai_key)
            self.model_name = "gpt-4o-mini"

    def analyze_trend(self, trend, **kwargs) -> ScriptAnalysis:
        desc = trend.description if hasattr(trend, 'description') else trend
        transcript = trend.transcript if hasattr(trend, 'transcript') else "N/A"
        hashtags = trend.hashtags if hasattr(trend, 'hashtags') else "N/A"
        
        prompt = f"""
        Act as a VIRAL SOCIAL MEDIA STRATEGIST.
        Analyze this topic for a cinematic video mission:
        Description: {desc}
        Transcript: {transcript}
        Hashtags: {hashtags}
        
        Target Tone: {kwargs.get('tone', 'Cinematic')}
        Target Platform: {kwargs.get('platform', 'TikTok')}
        
        Output valid JSON only with these keys:
        hook_technique, hook_variations (list of 3), emotional_trigger, structural_pattern, target_audience_insight, virality_score (1-10).
        """
        
        try:
            if self.use_gemini:
                response = self.model.generate_content(prompt)
                match = re.search(r'\{.*\}', response.text, re.DOTALL)
                data = json.loads(match.group()) if match else {}
            else:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                data = json.loads(response.choices[0].message.content)
            
            return ScriptAnalysis(**data)
        except Exception as e:
            print(f"Error analyzing trend: {e}")
            return ScriptAnalysis(
                hook_technique="Cinematic Storytelling",
                hook_variations=["The world is changing...", "Everything you knew was wrong.", "Watch until the end."],
                emotional_trigger="Awe",
                structural_pattern="Hero's Journey",
                target_audience_insight="General audience",
                virality_score=5
            )

    def generate_content(self, trend: TrendData, analysis: ScriptAnalysis, **kwargs) -> ContentDraft:
        prompt = f"""
        Act as a expert Cinematic Creative Director (Gemini).
        Trend Context: {trend.description if hasattr(trend, 'description') else trend}
        Strategic Analysis: {analysis.hook_technique}, {analysis.emotional_trigger}
        
        PARAMETERS:
        Tone: {kwargs.get('tone', 'Professional')}
        Duration: {kwargs.get('duration', 60)}s
        Platform: {kwargs.get('platform', 'TikTok')}
        
        TASKS:
        1. Write a high-end cinematic voiceover script ({kwargs.get('duration', 60)}s length).
        2. Plan scenes with detailed Character Actions and Camera Movements.
        3. Define a consistent 'visual_style_description'.
        
        Output VALID JSON matching this schema:
        {{
            "title": "string",
            "script": "string",
            "hook_selected": "string",
            "emotional_payoff": "string",
            "caption": "string",
            "visual_style_description": "string",
            "visual_prompt": "string",
            "music_mood_prompt": "string",
            "visual_scenes": [
                {{ "prompt": "string", "duration": float, "aspect_ratio": "string" }}
            ]
        }}
        """
        
        try:
            if self.use_gemini:
                response = self.model.generate_content(prompt)
                match = re.search(r'\{.*\}', response.text, re.DOTALL)
                data = json.loads(match.group()) if match else {}
            else:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                data = json.loads(response.choices[0].message.content)
            
            from models import Scene
            scenes = [Scene(**s) for s in data.get('visual_scenes', [])]
            
            return ContentDraft(
                title=data.get('title', 'Untitled'),
                hook_selected=data.get('hook_selected', ''),
                emotional_payoff=data.get('emotional_payoff', ''),
                script=data.get('script', ''),
                caption=data.get('caption', ''),
                visual_prompt=data.get('visual_prompt', ''),
                music_mood_prompt=data.get('music_mood_prompt', 'Ambient, cinematic background music'),
                visual_style_description=data.get('visual_style_description', 'High-end cinema'),
                visual_scenes=scenes
            )
        except Exception as e:
            print(f"Error generating content: {e}")
            return ContentDraft(
                title="Error Generating Content",
                script="Error",
                caption="Error",
                visual_prompt="Error",
                visual_style_description="Standard",
                visual_scenes=[]
            )
        except Exception as e:
            print(f"Error generating content: {e}")
            return ContentDraft(
                title="Error Generating Content",
                script="Error",
                caption="Error",
                visual_prompt="Error",
                is_aigc=True
            )

generator = ContentGenerator()
