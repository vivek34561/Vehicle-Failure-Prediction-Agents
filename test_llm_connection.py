
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

groq_key = os.environ.get("GROQ_API_KEY")
if not groq_key:
    print("GROQ_API_KEY not set in environment.")
    raise SystemExit(1)

url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {groq_key}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}
payload = {
    "model": "openai/gpt-oss-20b",
    "messages": [{"role": "user", "content": "Explain the importance of fast language models"}],
    "max_tokens": 512,
}

resp = requests.post(url, headers=headers, json=payload, timeout=30)
try:
    resp.raise_for_status()
    data = resp.json()
except Exception as e:
    print(f"Request failed: {e} - {resp.text}")
    raise

# Extract text from OpenAI-compatible response format
out = None
if isinstance(data, dict):
    try:
        if "choices" in data and len(data["choices"]) > 0:
            msg = data["choices"][0].get("message", {})
            out = msg.get("content")
    except Exception:
        pass

if not out:
    out = json.dumps(data, indent=2, default=str)

print(out)
