from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TrendData(BaseModel):
    """Data extracted from a TikTok trend."""
    video_id: str
    description: str
    hashtags: List[str]
    music_id: Optional[str] = None
    transcript: Optional[str] = None
    author: str
    url: str

class ScriptAnalysis(BaseModel):
    """Analysis of a trend by the Strategist Agent."""
    hook_technique: str = Field(description="The technique used in the hook (e.g., visual disruption, question).")
    hook_variations: List[str] = Field(default_factory=list, description="Top 3 variations of hooks to test.")
    emotional_trigger: str = Field(description="The primary emotion targeting the viewer.")
    structural_pattern: str = Field(description="The narrative structure of the video.")
    target_audience_insight: str
    virality_score: int = Field(description="Estimated virality score 1-10.")

class Scene(BaseModel):
    """A specific scene in the video."""
    prompt: str = Field(description="The cinematic visual prompt for this scene.")
    duration: float = Field(default=5.0, description="Suggested duration of this scene in seconds.")
    aspect_ratio: str = Field(default="9:16", description="Aspect ratio of the scene (9:16 for TikTok/Reels, 16:9 for YouTube).")

class ContentDraft(BaseModel):
    """Generated content script and details."""
    title: str
    script: str = Field(description="The long-form cinematic script.")
    hook_selected: str = Field(default="", description="The winning hook selected for this draft.")
    emotional_payoff: str = Field(default="", description="The specific value or emotion delivered at the end.")
    caption: str = Field(description="Optimized SEO caption with hashtags.")
    visual_prompt: str = Field(description="Primary prompt for fallback/preview.")
    visual_style_description: str = Field(default="Cinematic, high-definition, photorealistic, 8k.", description="Consistent visual style across all scenes.")
    visual_scenes: List[Scene] = Field(default_factory=list, description="List of cinematic scenes to be generated.")
    music_mood_prompt: str = Field(default="Ambient, cinematic background music", description="Prompt for background music generation.")
    image_url: Optional[str] = Field(default=None, description="Path to the generated visual preview.")
    video_url: Optional[str] = Field(default=None, description="Path or URL to the generated video.")
    is_aigc: bool = Field(default=True, description="Flag for TikTok compliance.")

class PostRecord(BaseModel):
    """Database record for a generated post."""
    id: Optional[str] = None
    topic: str
    tone: Optional[str] = "Professional"
    duration: Optional[int] = 60
    platform: Optional[str] = "TikTok"
    use_captions: Optional[bool] = True
    trend_source_url: Optional[str] = None
    analysis: Optional[ScriptAnalysis] = None
    draft: Optional[ContentDraft] = None
    status: str = Field(default="PENDING_APPROVAL", description="INITIALIZING, SEARCHING, ANALYZING, GENERATING, PENDING_APPROVAL, APPROVED, POSTED, REJECTED, ERROR")
    progress: int = Field(default=0, description="Overall completion percentage 0-100")
    created_at: datetime = Field(default_factory=datetime.now)
