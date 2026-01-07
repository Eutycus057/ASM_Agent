import os
import json
from tools.content_gen import generator
from models import TrendData, ScriptAnalysis

# Mock Trend
trend = TrendData(
    video_id="test_123",
    description="A viral video about tech productivity tools for 2024",
    hashtags=["productivity", "tech"],
    author="tech_tips",
    url="https://www.tiktok.com/@tech_tips/video/123456"
)

print("--- Testing analyze_trend ---")
try:
    analysis = generator.analyze_trend(trend)
    print("Success!")
    print(json.dumps(analysis.to_dict() if hasattr(analysis, "to_dict") else analysis.model_dump(), indent=2))
except Exception as e:
    print(f"FAILED: {e}")
