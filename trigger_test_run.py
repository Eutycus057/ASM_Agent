import requests
import json
import time

url = "http://127.0.0.1:8000/api/run-workflow"
payload = {
    "topic": "Write a short scene set in an African village where community disputes are resolved through a council of elders under a sacred tree. Show how storytelling, proverbs, collective listening, and reconciliation guide the process, emphasizing harmony, respect, and restoration rather than punishment.",
    "tone": "Peaceful/Philosophical",
    "duration": 60,
    "platform": "TikTok"
}

print(f"Triggering workflow for: {payload['topic']}")
response = requests.post(url, json=payload)

if response.status_code == 200:
    print("Workflow started successfully!")
    print(f"Response: {response.json()}")
else:
    print(f"Failed to start workflow: {response.status_code}")
    print(response.text)
