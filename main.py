from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from agents import app_graph
from models import PostRecord
from database import db
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

VERSION = "1.0.1-RESILIENT-IMPORTS"
app = FastAPI(title="Autonomous Social Media Agent", version=VERSION)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure frontend directory exists
os.makedirs("frontend", exist_ok=True)

class WorkflowRequest(BaseModel):
    topic: str
    tone: Optional[str] = "Professional"
    duration: Optional[int] = 60
    platform: Optional[str] = "TikTok"
    use_captions: Optional[bool] = True

class ApprovalRequest(BaseModel):
    action: str # "APPROVE" or "REJECT"

# --- API Endpoints ---

@app.get("/api/health")
def read_root():
    return {"status": "Social Media Agent is Active", "version": VERSION}

@app.get("/api/posts")
def get_posts():
    return db.get_all_posts()

@app.post("/api/run-workflow")
async def run_workflow(request: WorkflowRequest, background_tasks: BackgroundTasks):
    """
    Manually triggers the agent workflow for a given topic.
    Resumes if a failed mission with the same topic exists.
    """
    # Check for existing failed post to resume
    existing_post = db.find_failed_post_by_topic(request.topic)
    
    if existing_post:
        post_id = str(existing_post['id'])
        db.update_post_status(post_id, "INITIALIZING")
        print(f"Resuming existing failed workflow for topic: {request.topic} (ID: {post_id})")
    else:
        # Create initial shell record for live status tracking
        initial_post = PostRecord(
            topic=request.topic,
            tone=request.tone,
            duration=request.duration,
            platform=request.platform,
            use_captions=request.use_captions,
            trend_source_url="",
            status="INITIALIZING"
        )
        result = db.save_post(initial_post)
        post_id = result.get("id")
        print(f"Starting new workflow for topic: {request.topic} (ID: {post_id})")

    async def _run_agent(p_id: str):
        # Fetch current record to populate state for resumption
        current_data = db.get_post(p_id)
        if not current_data:
            print(f"Error: Post {p_id} not found in database.")
            return

        # Ensure we have all keys expected by AgentState
        initial_state = {
            "topic": request.topic,
            "tone": request.tone,
            "duration": request.duration,
            "platform": request.platform,
            "use_captions": request.use_captions,
            "trends": [],
            "selected_trend": None,
            "analysis": current_data.get('analysis'),
            "draft": current_data.get('draft'),
            "post_id": p_id,
            "voice_path": None,
            "music_path": None,
            "video_path": current_data.get('video_url'),
            "scene_video_paths": [],
            "error": None
        }
        
        try:
            # Run the agent graph
            result = await app_graph.ainvoke(initial_state)
            
            if result.get('error'):
                print(f"Workflow Finished with Error: {result['error']}")
                db.update_post_status(p_id, "ERROR")
            else:
                # PERSIST FINAL OUTPUTS
                if result.get('analysis'):
                    from models import ScriptAnalysis
                    analysis = result['analysis']
                    if isinstance(analysis, dict):
                        analysis = ScriptAnalysis(**analysis)
                    db.update_post_analysis(p_id, analysis)
                
                if result.get('draft'):
                    from models import ContentDraft
                    draft = result['draft']
                    if isinstance(draft, dict):
                        draft = ContentDraft(**draft)
                    db.update_post_draft(p_id, draft)

                if result.get('video_path'):
                    # Ensure video_url is updated if video_path is present
                    video_url = f"/assets/assets/animated_{p_id}.mp4"
                    db.update_post_video(p_id, video_url)

                db.update_post_status(p_id, "READY_FOR_APPROVAL")
                print(f"Workflow Finished Successfully for ID: {p_id}")
                
        except Exception as e:
            import traceback
            print(f"CRITICAL ERROR in WorkflowRunner (ID: {p_id}): {e}")
            traceback.print_exc()
            db.update_post_status(p_id, "ERROR")
    
    # Use asyncio.create_task instead of BackgroundTasks
    asyncio.create_task(_run_agent(post_id))
    return {"message": f"Workflow started for topic: {request.topic}", "post_id": post_id}

@app.post("/api/approve/{post_id}")
async def approve_post(post_id: str, request: ApprovalRequest, background_tasks: BackgroundTasks):
    """
    Simulates approval and publication.
    """
    db.update_post_status(post_id, "APPROVED")
    
    async def _post_to_tiktok():
        await asyncio.sleep(2)
        db.update_post_status(post_id, "PUBLISHED")
        print(f"Post {post_id} marked as Published")
        
    background_tasks.add_task(_post_to_tiktok)
    return {"message": "Post approved for publication"}

@app.delete("/api/posts/{post_id}")
async def delete_post(post_id: str):
    """
    Permanently removes a post from history.
    """
    db.delete_post(post_id)
    return {"message": "Post deleted successfully"}

# --- Static Files (Must be last) ---

app.mount("/assets", StaticFiles(directory="frontend"), name="assets")

@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
