import urllib.request
import json
import sys

BASE_URL = "http://localhost:8000"

def get_vehicles():
    try:
        with urllib.request.urlopen(f"{BASE_URL}/vehicles") as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print(f"Available vehicles: {data}")
                return data.get("vehicles", [])
    except Exception as e:
        print(f"Failed to get vehicles: {e}")
        return []

def test_query(vehicle_id):
    url = f"{BASE_URL}/query"
    payload = {
        "vehicle_id": vehicle_id,
        "query": "Is my car healthy? Any critical issues?"
    }
    
    encoded_data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=encoded_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"\nSending query for vehicle {vehicle_id}...")
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print("\nQuery Response:")
                print(json.dumps(data, indent=2))
            else:
                print(f"Query failed with status {response.status}")
                print(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
    except Exception as e:
        print(f"Query failed: {e}")

if __name__ == "__main__":
    vehicles = get_vehicles()
    if vehicles:
        # Use the first available vehicle
        target_vehicle = vehicles[0]
        test_query(target_vehicle)
    else:
        print("No vehicles found to query.")
