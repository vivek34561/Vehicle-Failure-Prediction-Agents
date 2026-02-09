import urllib.request
import json
import time
import sys

url = "http://localhost:8000/health"
max_retries = 5
for i in range(max_retries):
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print("Health check passed!")
                print(json.dumps(data, indent=2))
                sys.exit(0)
    except Exception as e:
        print(f"Attempt {i+1} failed: {e}")
        time.sleep(2)
else:
    print("Health check failed after multiple attempts.")
    sys.exit(1)
