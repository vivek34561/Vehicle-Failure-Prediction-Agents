# Vehicle Analysis & Maintenance System

AI-powered vehicle diagnostics, maintenance scheduling, and performance analysis using agentic AI with LLM-based routing.

---

## Overview

The Vehicle Analysis & Maintenance System is an AI-driven backend platform that analyzes real-time and historical vehicle sensor data.

A Master Agent interprets user intent and routes requests to specialized agents for diagnostics, maintenance, and performance analysis.

---

## Features

- FastAPI backend with Swagger UI  
- LLM-powered Master Agent  
- Diagnostic, Maintenance, and Performance agents  
- Intelligent query routing  
- JSON-based dataset for local testing  
- Historical analysis logs  
- Vercel-ready deployment  

---

## Tech Stack

- Python 3.10+  
- FastAPI  
- Gemini LLM API  
- Pydantic  
- Uvicorn  
- JSON-based local storage  

---

## System Architecture

User  
↓  
FastAPI Server  
↓  
Master Agent (LLM)  
↓  
Diagnostic Agent  
Maintenance Agent  
Performance Agent  
↓  
JSON Dataset and History Logs  

---

## Agent Responsibilities

### Master Agent
- Interprets user intent  
- Routes queries to appropriate agents  
- Aggregates and formats responses  

### Diagnostic Agent
- Detects anomalies  
- Validates sensor thresholds  
- Reports vehicle health and faults  

### Maintenance Agent
- Predicts service requirements  
- Estimates urgency  
- Recommends maintenance actions  

### Performance Agent
- Analyzes efficiency  
- Evaluates driving behavior  
- Suggests performance optimizations  

---

## Data Flow

1. User submits query  
2. Master Agent analyzes intent  
3. Specialized agent processes data  
4. Analysis logged to history  
5. Response returned to user  

---

## Quickstart

### Prerequisites

- Python 3.10+  
- Gemini API Key  

### Install Dependencies

```text
pip install -r requirements.txt
Configure Environment
text
Copy code
cp .env.example .env
GEMINI_API_KEY=your_gemini_api_key_here
Run Locally
text
Copy code
python main.py
Access API documentation at:
http://localhost:8000/docs

API Endpoints
Core
GET / — API information

GET /health — Health status

GET /vehicles — List all vehicles

GET /vehicle/{vehicle_id} — Full vehicle data

GET /history/{vehicle_id} — Historical analysis logs

AI-Powered
POST /query — AI-powered query routing

POST /analyze — Full vehicle analysis

/query Request Body
json
Copy code
{
  "vehicle_id": "VH001",
  "query": "Is my car healthy?"
}
/analyze Request Body
json
Copy code
{
  "vehicle_id": "VH001"
}
Examples
Python Client
python
Copy code
import requests

BASE = "http://localhost:8000"

response = requests.post(
    f"{BASE}/query",
    json={
        "vehicle_id": "VH001",
        "query": "Is my car healthy?"
    }
)

print(response.json())
cURL
text
Copy code
curl -X POST http://localhost:8000/query \
-H "Content-Type: application/json" \
-d '{"vehicle_id":"VH001","query":"Is my car healthy?"}'
Data & Sensors
Each vehicle record contains:

vehicle_id

car_type

available_sensor_fields

Common sensors include:

engine_temp_c

rpm

battery_voltage

battery_soc

oil_pressure_kpa

coolant_temp_c

fuel_level_percent

speed_kmph

tire_pressure

DTC fault codes

GPS coordinates

EV motor temperature

Reference ranges are defined in utils.py under SENSOR_RANGES.

Deployment (Vercel)
text
Copy code
npm i -g vercel
vercel deploy --prod
Set GEMINI_API_KEY as an environment variable.
File writes are ephemeral in serverless environments.

Security
Do not commit .env files

Always use .env.example

Rotate API keys immediately if exposed

To remove committed secrets:

text
Copy code
git rm --cached .env
git commit -m "Remove committed secrets"
Development & Contributing
text
Copy code
pip install -r requirements.txt
python main.py
Guidelines:

Follow PEP8

Use type hints

Keep agents modular

Never commit secrets

Project Structure
text
Copy code
.
├── main.py
├── agents_final.py
├── utils.py
├── monitor_cron.py
├── dataset/
│   └── vehicle_realtime_data.json
├── api/
│   └── index.py
├── requirements.txt
├── vercel.json
└── README.md
Future Enhancements
Persistent database (PostgreSQL or MongoDB)

Real-time telemetry ingestion

Alerts and notification system

Agent memory and learning loop

Web dashboard

Mobile application

OEM and IoT integrations

License

MIT License