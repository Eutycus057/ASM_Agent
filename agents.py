from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from models import TrendData, ScriptAnalysis, ContentDraft, PostRecord, Scene
from tools.scraper import fetch_trends
from tools.content_gen import generator
from database import db, TrendManager
from tools.audio_gen import audio_generator
from tools.animator import animator
from tools.video_gen import video_generator
from tools.music_gen import music_generator
import os

# Define the Agent State
class AgentState(TypedDict):
    topic: str
    tone: Optional[str]
    duration: Optional[int]
    platform: Optional[str]
    trends: List[TrendData]
    selected_trend: Optional[TrendData]
    analysis: Optional[ScriptAnalysis]
    draft: Optional[ContentDraft]
    post_id: Optional[str]
    voice_path: Optional[str]
    music_path: Optional[str]
    video_path: Optional[str]
    scene_video_paths: List[str]
    use_captions: Optional[bool]
    error: Optional[str]

# --- Nodes ---

async def trend_discovery_agent(state: AgentState):
    """
    Step 1: Discover context (optional but helpful for flavor).
    """
    print(f"--- Trend Discovery (Optional Context): {state['topic']} ---")
    post_id = state.get("post_id")
    if post_id:
        db.update_post_status(post_id, "SEARCHING")
        db.update_post_progress(post_id, 10)
        
    try:
        # Add a strict timeout to avoid browser hangs
        import asyncio
        trends = await asyncio.wait_for(fetch_trends(state['topic']), timeout=10.0)
        
        # If no trends, we still proceed with the topic itself
        return {"trends": trends, "selected_trend": trends[0] if trends else None}
    except Exception as e:
        print(f"Discovery Timeout or Error (Pivoting to Topic): {e}")
        # Return empty list to trigger topic-based generation
        return {"trends": [], "selected_trend": None}

async def creative_strategist_agent(state: AgentState):
    """
    Step 1: Generate educational/viral script.
    """
    print("--- Creative Strategist Scripting ---")
    post_id = state.get("post_id")
    # Resumption logic: if analysis already exists, skip
    if state.get("analysis"):
        print("Using existing strategic analysis.")
        analysis = state["analysis"]
        if isinstance(analysis, dict):
            analysis = ScriptAnalysis(**analysis)
        if post_id:
            db.update_post_progress(post_id, 20) # End of scripting stage
        return {"analysis": analysis}

    if post_id:
        db.update_post_status(post_id, "ANALYZING")
        db.update_post_progress(post_id, 5)
        
    # Generate high-quality script
    analysis = generator.analyze_trend(
        state.get('selected_trend') or state['topic'],
        tone=state.get('tone'),
        platform=state.get('platform')
    )
    if post_id:
        db.update_post_analysis(post_id, analysis)
        
    return {"analysis": analysis}

async def content_creator_agent(state: AgentState):
    """
    Step 2: Finalize Draft.
    """
    print("--- Content Creator Finalizing Draft ---")
    post_id = state.get("post_id")
    # Resumption logic: if draft already exists, skip
    if state.get("draft"):
        draft = state["draft"]
        if isinstance(draft, dict):
            draft = ContentDraft(**draft)
        if draft.visual_scenes:
            print("Using existing content draft.")
            if post_id:
                db.update_post_progress(post_id, 40) # End of draft stage
            return {"draft": draft}

    if post_id:
        db.update_post_status(post_id, "GENERATING")
        db.update_post_progress(post_id, 25)
        
    draft = generator.generate_content(
        state.get('selected_trend') or state['topic'], 
        state['analysis'],
        tone=state.get('tone'),
        duration=state.get('duration'),
        platform=state.get('platform')
    )
    if post_id:
        db.update_post_draft(post_id, draft)
        
    return {"draft": draft}

async def voice_generation_agent(state: AgentState):
    """
    Step 3: Generate Audio (TTS).
    """
    print("--- Voice Generation (TTS) ---")
    post_id = state.get("post_id")
    filename = f"voice_{post_id}.mp3"
    audio_path = os.path.join("frontend/assets", filename)
    
    # Resumption logic: check if file exists
    if os.path.exists(audio_path):
        print(f"Using existing voiceover: {audio_path}")
        if post_id:
            db.update_post_progress(post_id, 60) # End of voice stage
        return {"voice_path": audio_path}

    if post_id:
        db.update_post_status(post_id, "VOICE")
        db.update_post_progress(post_id, 45)
    
    script_text = state['draft'].script
    
    # Use OpenAI TTS (with Edge TTS fallback)
    audio_path = await audio_generator.generate_speech_async(script_text, filename)
    
    if not audio_path:
        return {"error": "Voice generation failed"}
        
    return {"voice_path": audio_path}

async def animation_orchestrator_agent(state: AgentState):
    """
    Step 5: Create Multi-Scene Cinematic Video.
    """
    print("--- Multi-Scene Cinematic Animation Orchestration ---")
    post_id = state.get("post_id")
    if post_id:
        db.update_post_status(post_id, "ANIMATION")
        db.update_post_progress(post_id, 65)
    
    scenes = state['draft'].visual_scenes
    visual_style = state['draft'].visual_style_description
    if not scenes:
        print("No scenes found, falling back to primary visual prompt.")
        scenes = [Scene(prompt=state['draft'].visual_prompt, duration=5.0)]

    scene_video_paths = []
    
    for i, scene in enumerate(scenes):
        print(f"--- Processing Scene {i+1}/{len(scenes)} ---")
        scene_base_image = f"frontend/assets/scene_{post_id}_{i}.png"
        scene_raw_video = f"frontend/assets/scene_raw_{post_id}_{i}.mp4"
        
        # Resumption logic for scene video
        if os.path.exists(scene_raw_video):
            print(f"Using existing scene video: {scene_raw_video}")
            scene_video_paths.append(scene_raw_video)
            continue

        # Step A: Generate Base Image
        # Pass the global visual style for consistency
        image_path = video_generator.generate_base_image(
            f"{scene.prompt} | STYLE: {visual_style}", 
            scene_base_image
        )
        if not image_path:
            continue
            
        # Step B: Generate SVD Video (or Ken Burns fallback)
        # Pass the scene duration and aspect ratio
        video_raw_path = video_generator.generate_video(
            image_path, 
            scene_raw_video, 
            duration=scene.duration,
            aspect_ratio=getattr(scene, 'aspect_ratio', '9:16')
        )
        if video_raw_path:
            scene_video_paths.append(video_raw_path)
    
    if not scene_video_paths:
        if post_id: db.update_post_status(post_id, "ERROR")
        return {"error": "Multi-scene generation failed completely"}
    
    # Step B: Generate Background Music (Stable Audio 2.5)
    music_mood = state['draft'].music_mood_prompt
    music_file = f"music_{post_id}.mp3"
    music_path = f"frontend/assets/{music_file}"
    
    # Estimate total duration needed (sum of scene durations)
    total_duration = sum([s.duration for s in scenes])
    
    music_path_result = music_generator.generate_background_music(music_mood, music_path, duration=int(total_duration))
    
    # Step C: Assemble Final Video with Dual Audio (Concatenating clips + mix)
    final_video = f"animated_{post_id}.mp4"
    video_path = animator.assemble_multi_scene_video(
        scene_video_paths, 
        state['voice_path'], 
        final_video,
        music_path=music_path_result
    )
    
    if not video_path:
        if post_id: db.update_post_status(post_id, "ERROR")
        return {"error": "Multi-scene video assembly failed"}
        
    video_url = f"/assets/assets/animated_{post_id}.mp4"
    
    if post_id:
        db.update_post_video(post_id, video_url)
        db.update_post_status(post_id, "PENDING_APPROVAL")
        db.update_post_progress(post_id, 100)
        
    return {
        "video_path": video_path, 
        "scene_video_paths": scene_video_paths,
        "music_path": music_path_result
    }

# --- Graph Definition ---

workflow = StateGraph(AgentState)

workflow.add_node("discovery", trend_discovery_agent)
workflow.add_node("strategist", creative_strategist_agent)
workflow.add_node("creator", content_creator_agent)
workflow.add_node("voice", voice_generation_agent)
workflow.add_node("animation", animation_orchestrator_agent)

workflow.set_entry_point("strategist")

workflow.add_edge("strategist", "creator")
workflow.add_edge("creator", "voice")
workflow.add_edge("voice", "animation")
workflow.add_edge("animation", END)

app_graph = workflow.compile()
