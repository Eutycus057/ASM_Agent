import requests
import time
import sys

def trigger():
    url = "http://localhost:8000/api/run-workflow"
    payload = {"topic": "AI Automation"}
    
    try:
        print(f"Triggering workflow at {url}...")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Success:", response.json())
        
        # Wait for background task
        print("Waiting 15 seconds for background task details...")
        time.sleep(15)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    trigger()
