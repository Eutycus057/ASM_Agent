import os
from dotenv import load_dotenv

load_dotenv()

def check_key(name):
    val = os.environ.get(name)
    if val:
        print(f"{name}: FOUND ({val[:4]}...{val[-4:]})")
    else:
        print(f"{name}: NOT FOUND")

check_key("OPENAI_API_KEY")
check_key("STABILITY_API_KEY")
check_key("LLM_API_KEY")
