import os
from openai import OpenAI

api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello, are you there?"}]
    )
    print("LLM Response:", response.choices[0].message.content)
except Exception as e:
    print("LLM Error:", e)
