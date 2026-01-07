import os
import sqlite3
import json
from datetime import datetime
from dotenv import load_dotenv
from models import PostRecord, TrendData, ScriptAnalysis, ContentDraft

load_dotenv()

class Database:
    def __init__(self):
        self.db_path = os.environ.get("DATABASE_PATH", "./prototype_data.db")
        self.init_db()

    def init_db(self):
        """Initialize the SQLite database with the posts table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                trend_source_url TEXT,
                analysis TEXT,
                draft TEXT,
                image_url TEXT,
                video_url TEXT,
                status TEXT,
                use_captions INTEGER DEFAULT 1,
                progress INTEGER DEFAULT 0,
                created_at TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def save_post(self, post: PostRecord):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Serialize nested Pydantic models to JSON (safe for None)
        analysis_json = post.analysis.model_dump_json() if post.analysis else None
        draft_json = post.draft.model_dump_json() if post.draft else None
        created_at_str = post.created_at.isoformat()
        
        cursor.execute('''
            INSERT INTO posts (topic, trend_source_url, analysis, draft, image_url, video_url, status, use_captions, progress, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (post.topic, post.trend_source_url, analysis_json, draft_json, post.draft.image_url if post.draft else None, post.draft.video_url if post.draft else None, post.status, 1 if post.use_captions else 0, post.progress, created_at_str))
        
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {"id": str(post_id), "status": "success"}

    def check_duplicate_trend(self, video_id: str) -> bool:
        """Check if a trend from this video URL has already been used."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM posts WHERE trend_source_url = ?', (video_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def update_post_status(self, post_id: str, status: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE posts SET status = ? WHERE id = ?', (status, post_id))
        conn.commit()
        conn.close()

    def update_post_analysis(self, post_id: str, analysis: ScriptAnalysis):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE posts SET analysis = ? WHERE id = ?', (analysis.model_dump_json(), post_id))
        conn.commit()
        conn.close()

    def update_post_draft(self, post_id: str, draft: ContentDraft):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE posts SET draft = ?, image_url = ?, video_url = ? WHERE id = ?', (draft.model_dump_json(), draft.image_url, draft.video_url, post_id))
        conn.commit()
        conn.close()

    def update_post_image(self, post_id: str, image_url: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE posts SET image_url = ? WHERE id = ?', (image_url, post_id))
        conn.commit()
        conn.close()

    def update_post_video(self, post_id: str, video_url: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE posts SET video_url = ? WHERE id = ?', (video_url, post_id))
        conn.commit()
        conn.close()

    def delete_post(self, post_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
        conn.close()

    def get_post(self, post_id: str):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        post_dict = dict(row)
        try:
            if post_dict['analysis']:
                post_dict['analysis'] = json.loads(post_dict['analysis'])
        except:
            pass
        try:
            if post_dict['draft']:
                post_dict['draft'] = json.loads(post_dict['draft'])
        except:
            pass
        
        post_dict['use_captions'] = bool(post_dict.get('use_captions', 1))
        return post_dict

    def find_failed_post_by_topic(self, topic: str):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM posts WHERE topic = ? AND status = "ERROR" ORDER BY created_at DESC LIMIT 1', (topic,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        return self.get_post(str(row['id']))

    def get_all_posts(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM posts ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        posts = []
        for row in rows:
            post_dict = dict(row)
            # Parse JSON strings back to dicts
            try:
                if post_dict['analysis']:
                    post_dict['analysis'] = json.loads(post_dict['analysis'])
            except:
                pass
            try:
                if post_dict['draft']:
                    post_dict['draft'] = json.loads(post_dict['draft'])
            except:
                pass
            
            # Convert INTEGER to boolean for use_captions
            post_dict['use_captions'] = bool(post_dict.get('use_captions', 1))
            
            posts.append(post_dict)
            
        conn.close()
        return posts

    def update_post_status(self, post_id: str, status: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE posts SET status = ? WHERE id = ?', (status, post_id))
        conn.commit()
        conn.close()

    def update_post_progress(self, post_id: str, progress: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE posts SET progress = ? WHERE id = ?', (progress, post_id))
        conn.commit()
        conn.close()

db = Database()

class TrendManager:
    def __init__(self, database: Database):
        self.db = database

    def is_new_trend(self, trend: TrendData) -> bool:
        # Check against database based on video URL
        return not self.db.check_duplicate_trend(trend.url)
    
    def save_draft(self, post: PostRecord):
        return self.db.save_post(post)
