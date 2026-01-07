import asyncio
import os
from agents import app_graph
from database import db
from models import PostRecord

async def test_full_flow():
    topic = "The Future of Quantum Computing"
    print(f"--- Starting Test Workflow: {topic} ---")
    
    # Create initial shell record
    initial_post = PostRecord(
        topic=topic,
        trend_source_url="http://test.com",
        status="INITIALIZING"
    )
    result = db.save_post(initial_post)
    post_id = result.get("id")

    initial_state = {
        "topic": topic,
        "trends": [],
        "selected_trend": None,
        "analysis": None,
        "draft": None,
        "post_id": post_id,
        "error": None,
        "voice_path": None,
        "video_path": None,
        "base_image_path": None,
        "raw_video_path": None
    }

    try:
        final_state = await app_graph.ainvoke(initial_state)
        print("\n--- Workflow Results ---")
        print(f"Post ID: {post_id}")
        if final_state.get("error"):
            print(f"Error: {final_state['error']}")
        else:
            print(f"Title: {final_state['draft'].title}")
            print(f"Voice Path: {final_state['voice_path']}")
            print(f"Music Path: {final_state.get('music_path')}")
            print(f"Scene Video Paths: {final_state.get('scene_video_paths', [])}")
            print(f"Final Video Path: {final_state['video_path']}")
            print("SUCCESS")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_full_flow())
