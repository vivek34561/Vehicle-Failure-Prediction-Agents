
import requests
import json
import sys
import os
from dotenv import load_dotenv
import time

# The key found in agents_final.py
API_KEY = "ff79bbc8103b418ca138a15734256bab.cf3FccbTvaGzs4PXIz8AHblp"
GROQ_BASE = "https://api.groq.com/openai/v1"

def check_groq():
    """
    Test Groq (Groq.ai) connectivity using the OpenAI-compatible client.
    """
    print("\n--- Testing Groq (GROQ_API_KEY) ---")
    load_dotenv()
    groq_key = os.environ.get("GROQ_API_KEY")
    if not groq_key:
        print("GROQ_API_KEY not set in environment (.env or system env).")
        return False

    try:
        # Direct HTTP call to Groq's OpenAI-compatible chat completions endpoint
        url = f"{GROQ_BASE}/chat/completions"
        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "model": "openai/gpt-oss-20b",
            "messages": [{"role": "user", "content": "Test"}],
            "max_tokens": 256
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        # Try to extract response text from OpenAI-compatible response
        out = None
        if isinstance(data, dict):
            try:
                if "choices" in data and len(data["choices"]) > 0:
                    msg = data["choices"][0].get("message", {})
                    out = msg.get("content")
            except Exception:
                pass

        if out:
            print("Groq response text:", out)
        else:
            print("Groq response:")
            try:
                print(json.dumps(data, indent=2, default=str))
            except Exception:
                print(str(data))

        print(">> Groq connectivity OK.")
        return True
    except requests.exceptions.HTTPError as e:
        # Surface HTTP errors (including 429 rate limit)
        status = getattr(e.response, "status_code", None)
        print(f"Groq HTTP error (status={status}): {e}")
        # If rate limited, optionally wait a bit and retry once
        if status == 429:
            retry_after = int(e.response.headers.get("Retry-After", "5"))
            print(f"Rate limited by Groq; retrying after {retry_after}s...")
            time.sleep(retry_after)
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=20)
                resp.raise_for_status()
                print(">> Groq connectivity OK on retry.")
                return True
            except Exception as e2:
                print(f"Retry failed: {e2}")
        return False
    except Exception as e:
        print(f"Error connecting to Groq: {e}")
        return False

if __name__ == "__main__":
    check_groq()
