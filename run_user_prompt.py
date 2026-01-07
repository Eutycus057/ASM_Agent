import requests

def run_prompt():
    url = "http://localhost:8000/api/run-workflow"
    topic = """In a rural African village where tradition governs both love and legacy, two families gather beneath an ancient tree for a dowry negotiation that will determine the future of a young couple deeply in love. Elders debate livestock, land, and symbolic gifts, each demand carrying generations of meaning and unspoken pride. As tensions rise and voices harden, hidden family secrets, economic pressures, and the couple’s quiet resistance begin to surface. Write a story that explores how culture, honor, and modern aspirations collide during this single, decisive afternoon—and whether love can reshape a tradition without breaking it"""
    
    payload = {"topic": topic}
    
    try:
        print(f"Triggering workflow with user prompt...")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Success:", response.json())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_prompt()
