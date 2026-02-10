
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

groq_key = os.environ.get("GROQ_API_KEY")
if not groq_key:
    print("GROQ_API_KEY not set in environment.")
    raise SystemExit(1)

url = "https://api.groq.com/openai/v1/responses"
headers = {
    "Authorization": f"Bearer {groq_key}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}
payload = {
    "model": "openai/gpt-oss-20b",
    "input": "Explain the importance of fast language models",
    "max_output_tokens": 512,
}

resp = requests.post(url, headers=headers, json=payload, timeout=30)
try:
    resp.raise_for_status()
    data = resp.json()
except Exception as e:
    print(f"Request failed: {e} - {resp.text}")
    raise

# Extract text from several possible response shapes
out = None
if isinstance(data, dict):
    out = data.get("output_text")
    if not out and "output" in data:
        parts = []
        for item in data.get("output", []):
            for c in item.get("content", []):
                text = c.get("text") or c.get("body") or c.get("content")
                if isinstance(text, str):
                    parts.append(text)
        if parts:
            out = "".join(parts)

if not out:
    out = json.dumps(data, indent=2, default=str)

print(out)
