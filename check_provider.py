
import requests
import json
import sys

# The key found in agents_final.py
API_KEY = "ff79bbc8103b418ca138a15734256bab.cf3FccbTvaGzs4PXIz8AHblp"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def check_openrouter():
    print(f"--- Testing OpenRouter API Key ---")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000", # Required by OpenRouter sometimes
        "X-Title": "VehicleAgents"
    }
    data = {
        "model": "x-ai/grok-3-mini",
        "messages": [{"role": "user", "content": "Test"}]
    }
    
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=10)
        print(f"Status Code: {response.status_code}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Raw Response: {response.text}")
            
        if response.status_code == 200:
            print(">> OpenRouter Key is VALID.")
            return True
        else:
            print(">> OpenRouter Key is INVALID or Quota Exceeded.")
            return False
    except Exception as e:
        print(f"Error connecting to OpenRouter: {e}")
        return False

def check_ollama():
    print(f"\n--- Testing Local Ollama Status ---")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print(f"Ollama is RUNNING. Available models:")
            try:
                models = response.json().get('models', [])
                for m in models:
                    print(f" - {m.get('name')}")
            except:
                print("Could not parse model list.")
            return True
        else:
            print(f"Ollama responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(">> Ollama is NOT reachable at localhost:11434 (Connection Refused).")
        return False
    except Exception as e:
        print(f"Error checking Ollama: {e}")
        return False

if __name__ == "__main__":
    check_openrouter()
    check_ollama()
