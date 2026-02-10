
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
        # Direct HTTP call to Groq's OpenAI-compatible Responses endpoint
        url = f"{GROQ_BASE}/responses"
        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "model": "openai/gpt-oss-20b",
            "input": "Test",
            "max_output_tokens": 256
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        # Try several common places for response text
        out = None
        if isinstance(data, dict):
            out = data.get("output_text")
            if not out and "output" in data:
                try:
                    parts = []
                    for item in data.get("output", []):
                        for c in item.get("content", []):
                            text = c.get("text") or c.get("body") or c.get("content")
                            if isinstance(text, str):
                                parts.append(text)
                    if parts:
                        out = "".join(parts)
                except Exception:
                    out = None

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

def check_groq():
    """
    Test Groq (Groq.ai) connectivity using the official OpenAI-compatible client.
    Replaces local Ollama check with a GROQ API call that verifies the API key.
    """
    print("\n--- Testing Groq (GROQ_API_KEY) ---")
    load_dotenv()
    groq_key = os.environ.get("GROQ_API_KEY")
    if not groq_key:
        print("GROQ_API_KEY not set in environment (.env or system env).")
        return False

    try:
        client = OpenAI(api_key=groq_key, base_url="https://api.groq.com/openai/v1")
        # Lightweight sanity request
        resp = client.responses.create(
            input="Test",
            model="openai/gpt-oss-20b",
            max_output_tokens=256
        )

        # Print a short summary
        try:
            # Some client versions expose `output_text`
            out = getattr(resp, "output_text", None) or (resp.get("output_text") if isinstance(resp, dict) else None)
            if out:
                print("Groq response text:", out)
            else:
                # Fallback: pretty-print the response object
                print("Groq response:")
                try:
                    print(json.dumps(resp, indent=2, default=str))
                except Exception:
                    print(str(resp))
        except Exception:
            print("Received Groq response (unable to pretty-print).")

        print(">> Groq connectivity OK.")
        return True
    except Exception as e:
        print(f"Error connecting to Groq: {e}")
        return False

if __name__ == "__main__":
    check_groq()
