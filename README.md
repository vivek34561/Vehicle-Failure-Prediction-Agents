# Vehicle Analysis & Maintenance System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

AI-powered vehicle diagnostics, maintenance scheduling, and performance analysis using an **agentic AI architecture** with LLM-powered specialized agents.

---

## Table of Contents

- Overview
- Features
- Tech Stack
- System Architecture
- Agent Responsibilities
- Data Flow
- Quickstart
- API Endpoints
- Examples
- Data & Sensors
- Deployment (Vercel)
- Security
- Development & Contributing
- Project Structure
- Future Enhancements
- License

---

## Overview

The **Vehicle Analysis & Maintenance System** is an AI-driven backend platform that analyzes real-time and historical vehicle sensor data to deliver intelligent insights.

It uses a **Master Agent** to understand user intent and route queries to the most appropriate specialized agent:

- Diagnostic Agent
- Maintenance Agent
- Performance Agent

This project demonstrates **agentic AI**, **system design**, and **LLM orchestration**, making it suitable for production, research, hackathons, and resumes.

---

## Features

- FastAPI backend with Swagger UI
- LLM-powered Master Agent
- Diagnostic, Maintenance, and Performance agents
- Intelligent query routing
- JSON-based dataset for local testing
- Historical analysis logging

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Copy the example environment file and set `GEMINI_API_KEY`. Choose the commands that match your environment:

Linux / macOS:
```bash
cp .env.example .env
# session-only
export GEMINI_API_KEY='your-api-key-here'
```

Windows PowerShell (session-only):
```powershell
Copy-Item .env.example .env
$env:GEMINI_API_KEY = 'your-api-key-here'
```

Windows PowerShell (persist):
```powershell
Copy-Item .env.example .env
setx GEMINI_API_KEY "your-api-key-here"
# open a new shell to see the persistent variable
```

Windows CMD (session-only):
```cmd
copy .env.example .env
set GEMINI_API_KEY=your-api-key-here
```

### Run Locally

Start the server:

```bash
python main.py
```

Server will be available at `http://localhost:8000` and the interactive docs at `http://localhost:8000/docs`.

Stopping the server:

- Press `Ctrl+C` in the terminal running the server to stop it.
- If it doesn't stop, on Windows PowerShell you can run: `Get-Process python | Stop-Process -Force`.

Run in background (PowerShell example):

```powershell
Start-Process -NoNewWindow -FilePath python -ArgumentList 'main.py'
```

Alternative (run with Uvicorn directly):

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
▼
FastAPI Server
│
▼
Master Agent (LLM)
│
├── Diagnostic Agent
│── Maintenance Agent
│── Performance Agent
│
▼
JSON Dataset & History Logs

yaml
## API Endpoints

Core endpoints:

- `GET /` — API information
- `GET /health` — Health status and total vehicles
- `GET /vehicles` — List all vehicle IDs
- `GET /vehicle/{vehicle_id}` — Full vehicle data (see `dataset/vehicle_realtime_data.json` for available fields)
- `GET /history/{vehicle_id}` — Historical analysis logs (query param `limit` optional)

AI-powered endpoints:

- `POST /query`

  Request body JSON:

  ```json
  {
    "vehicle_id": "VH001",
    "query": "Is my car healthy?"
  }
  ```

  Response JSON example:

  ```json
  {
    "vehicle_id": "VH001",
    "agent_used": "diagnostic",
    "response": "Vehicle operating within safe limits.",
    "timestamp": "2025-01-01T10:15:00"
  }
  ```

- `POST /analyze`

  Request body JSON:

  ```json
  {
    "vehicle_id": "VH001"
  }
  ```

  Returns a combined analysis object containing `diagnostic`, `maintenance`, and `performance` text outputs from each agent.
## Quickstart

### Prerequisites

- Python 3.10+
- Gemini API Key

---

### Install Dependencies

```bash
pip install -r requirements.txt
Configure Environment Variables
bash
Copy code
cp .env.example .env
env
Copy code
GEMINI_API_KEY=your_gemini_api_key_here
Run Locally
bash
Copy code
python main.py
Open in browser:

bash
Copy code
http://localhost:8000/docs
API Endpoints
Core Endpoints
Method	Endpoint	Description
GET	/	API information
GET	/health	Health status
GET	/vehicles	List all vehicles
GET	/vehicle/{vehicle_id}	Full vehicle data
GET	/history/{vehicle_id}	Historical analysis logs

AI-Powered Endpoints
POST /query
Request body:

json
Copy code
{
  "vehicle_id": "VH001",
  "query": "Is my car healthy?"
}
Response:

json
Copy code
{
  "vehicle_id": "VH001",
  "agent_used": "diagnostic",
  "response": "Vehicle operating within safe limits.",
  "timestamp": "2025-01-01T10:15:00"
}
POST /analyze
Request body:

json
Copy code
{
  "vehicle_id": "VH001"
}
Returns combined diagnostic, maintenance, and performance analysis.

## Examples

Python client example (requests):

```python
import requests

BASE_URL = "http://localhost:8000"

response = requests.post(
    f"{BASE_URL}/query",
    json={
        "vehicle_id": "VH001",
        "query": "Do I need maintenance soon?"
    }
)

print(response.json())
```

cURL example:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"vehicle_id":"VH001","query":"Is my car healthy?"}'
```

## Data & Sensors

Each vehicle record (see `dataset/vehicle_realtime_data.json`) contains:

- `vehicle_id` (string)
- `car_type` (string)
- `available_sensor_fields` (object mapping sensor names to values)

Common sensors include:

- `engine_temp_c` (°C)
- `rpm`
- `battery_voltage`
- `battery_soc` (percent)
- `oil_pressure_kpa`
- `coolant_temp_c`
- `fuel_level_percent`
- `speed_kmph`
- Tire pressures: `tire_pressure_fl`, `tire_pressure_fr`, etc.
- `dtc_codes` (list of diagnostic trouble codes)
- `gps_lat`, `gps_lon`
- EV-specific: `motor_temp_c`, `inverter_temp_c`, `charger_state`

Sensor reference ranges are defined in `utils.py` as `SENSOR_RANGES`.

## Deployment (Vercel)

This project includes a Vercel-compatible API entrypoint (`api/index.py`) and `vercel.json`.

To deploy:

```bash
npm i -g vercel
vercel deploy --prod
```

Add `GEMINI_API_KEY` as a Vercel Environment Variable. Note that local file writes are ephemeral in serverless environments; use external storage (S3, database, or Vercel KV) for persistence.

## Security

- Never commit `.env` files. Keep a `.env.example` in the repo.
- Rotate API keys immediately if exposed.

To remove committed secrets:

```bash
git rm --cached .env
git commit -m "Remove committed secrets"
```

## Development & Contributing

Local development:

```bash
pip install -r requirements.txt
python main.py
```

Guidelines:

- Follow PEP8
- Use type hints
- Keep agents modular
- Do not commit secrets

Adding a new agent:

1. Implement agent logic in `agents_final.py`
2. Update master agent routing
3. Test using `/query`

## Project Structure

```
.
├── main.py                 # FastAPI app
├── agents_final.py         # Agent logic & routing
├── utils.py                # Sensor ranges & data manager
├── monitor_cron.py         # Scheduled monitoring
├── dataset/
│   └── vehicle_realtime_data.json
├── api/
│   └── index.py            # Vercel entrypoint
├── requirements.txt
├── vercel.json
└── README.md
```

## Future Enhancements

- Persistent database (PostgreSQL / MongoDB)
- Real-time telemetry ingestion
- Alerting & notification system
- Agent memory and learning loop
- Dashboard frontend (React)
- Mobile application (React Native)
- OEM & IoT integrations

## License

MIT License