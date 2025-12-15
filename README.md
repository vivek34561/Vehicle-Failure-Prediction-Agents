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
- Vercel-ready serverless deployment

---

## Tech Stack

- Python 3.10+
- FastAPI
- Gemini LLM API
- Pydantic
- Uvicorn
- JSON (local data storage)

---

## System Architecture

### High-Level Design

User
│
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
Copy code

---

## Agent Responsibilities

### Master Agent
- Understands user intent using LLM reasoning
- Routes queries to the correct specialist agent
- Aggregates and formats responses

### Diagnostic Agent
- Detects anomalies in sensor data
- Checks sensor values against safe thresholds
- Identifies faults and health risks

### Maintenance Agent
- Predicts upcoming service requirements
- Estimates urgency and priority
- Recommends maintenance actions

### Performance Agent
- Analyzes driving efficiency
- Evaluates vehicle performance
- Suggests optimization improvements

---

## Data Flow

1. User sends a query
2. Master Agent interprets intent
3. Specialized agent analyzes vehicle data
4. Result is logged to history
5. Final response returned to user

---

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

Examples
Python Client
python
Copy code
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
cURL
bash
Copy code
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"vehicle_id":"VH001","query":"Is my car healthy?"}'
Data & Sensors
Each vehicle record contains:

vehicle_id

car_type

available_sensor_fields

Common Sensors
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

Sensor reference ranges are defined in:

Copy code
utils.py → SENSOR_RANGES
Deployment (Vercel)
This project includes:

vercel.json

api/index.py (ASGI adapter)

Deploy
bash
Copy code
npm i -g vercel
vercel deploy --prod
Add GEMINI_API_KEY as a Vercel Environment Variable.

Notes
Local file writes are ephemeral in serverless environments

Use external storage (S3, database, Vercel KV) for persistence

Scheduled monitoring requires Vercel Cron Jobs or external scheduler

Security
Never commit .env files

Always use .env.example

Rotate API keys immediately if exposed

To remove committed secrets:

bash
Copy code
git rm --cached .env
git commit -m "Remove committed secrets"
Development & Contributing
Local Development
bash
Copy code
pip install -r requirements.txt
python main.py
Contribution Guidelines
Follow PEP8

Use type hints

Keep agents modular

Do not commit secrets

Adding a New Agent
Implement agent logic in agents_final.py

Update Master Agent routing

Test using /query

Project Structure
bash
Copy code
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
Future Enhancements
Persistent database (PostgreSQL / MongoDB)

Real-time telemetry ingestion

Alerting & notification system

Agent memory and learning loop

Dashboard frontend (React)

Mobile application (React Native)

OEM & IoT integrations

License
MIT License