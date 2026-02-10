
import requests
import json
import sys
import os
from dotenv import load_dotenv
from openai import OpenAI

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
        client = OpenAI(api_key=groq_key, base_url=GROQ_BASE)
        # Lightweight sanity request
        resp = client.responses.create(
            input="Test",
            model="openai/gpt-oss-20b",
            max_output_tokens=256
        )

        # Print a short summary
        try:
            out = getattr(resp, "output_text", None) or (resp.get("output_text") if isinstance(resp, dict) else None)
            if out:
                print("Groq response text:", out)
            else:
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
