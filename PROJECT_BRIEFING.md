# Vehicle Failure Prediction Agents - Complete Project Briefing

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Workflow & Data Flow](#workflow--data-flow)
4. [File-by-File Breakdown](#file-by-file-breakdown)
5. [Input/Output Schemas](#inputoutput-schemas)
6. [Agent System Details](#agent-system-details)
7. [API Endpoints Reference](#api-endpoints-reference)
8. [Data Structures](#data-structures)

---

## 🎯 Project Overview

**Vehicle Analysis & Maintenance System** is an AI-powered backend platform that:
- Analyzes real-time vehicle sensor data
- Provides intelligent diagnostics, maintenance recommendations, and performance insights
- Uses an **agentic AI architecture** with specialized LLM-powered agents
- Routes user queries intelligently to the most appropriate specialist agent

**Tech Stack:**
- **Backend Framework:** FastAPI (Python)
- **AI/LLM:** Google Gemini 2.0 Flash (via PydanticAI)
- **Data Storage:** JSON files (local, can be extended to databases)
- **Deployment:** Vercel-ready

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Server (main.py)                 │
│                  Port 8000, CORS enabled                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Master Agent (agents_final.py)                  │
│         Routes queries to appropriate specialist             │
└──────┬───────────────┬───────────────┬──────────────────────┘
       │               │               │
       ▼               ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Diagnostic  │ │ Maintenance │ │ Performance │
│   Agent     │ │    Agent    │ │    Agent    │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘
       │               │               │
       └───────────────┴───────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         VehicleDataManager (utils.py)                       │
│         Reads from dataset/vehicle_realtime_data.json       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Workflow & Data Flow

### 1. **Query Workflow** (`POST /query`)

```
User Query
    │
    ▼
FastAPI Endpoint (/query)
    │
    ▼
Master Agent (route_query)
    │
    ├─ Analyzes query intent
    │
    ├─ Routes to: Diagnostic / Maintenance / Performance
    │
    ▼
Specialized Agent
    │
    ├─ Uses tools to fetch vehicle data
    ├─ Analyzes sensor readings
    ├─ Generates LLM-powered response
    │
    ▼
Response + Logging
    │
    ├─ Returns to user
    └─ Saves to AnalysisLogger
```

### 2. **Comprehensive Analysis Workflow** (`POST /analyze`)

```
Vehicle ID
    │
    ▼
FastAPI Endpoint (/analyze)
    │
    ▼
get_comprehensive_analysis()
    │
    ├─ Runs Diagnostic Agent (parallel)
    ├─ Runs Maintenance Agent (parallel)
    └─ Runs Performance Agent (parallel)
    │
    ▼
Combined Analysis Result
    │
    ├─ Returns all three analyses
    └─ Logs complete report
```

### 3. **Monitoring Workflow** (`monitor_cron.py`)

```
Cron Job Trigger (hourly)
    │
    ▼
MonitoringService.monitor_all_vehicles()
    │
    ├─ For each vehicle:
    │   ├─ Check critical sensors
    │   ├─ Run comprehensive analysis
    │   ├─ Generate monitoring report
    │   └─ Save alerts if critical issues found
    │
    ▼
Monitoring Reports & Alerts
    │
    ├─ dataset/monitoring_reports.json
    └─ dataset/alerts.json
```

---

## 📁 File-by-File Breakdown

### **1. `main.py` - FastAPI Application Entry Point**

**Purpose:** Main web server and API endpoints

**Key Components:**
- FastAPI app initialization with CORS middleware
- Request/Response models (Pydantic schemas)
- API endpoints for vehicle queries and analysis
- Error handling and validation

**Key Functions:**
- `root()` - API information endpoint
- `health_check()` - Health status
- `list_vehicles()` - Get all vehicle IDs
- `get_vehicle_data()` - Fetch specific vehicle data
- `query_vehicle()` - **Main query endpoint** - routes to agents
- `comprehensive_analysis()` - **Full analysis endpoint** - runs all agents
- `get_vehicle_history()` - Historical analysis logs

**Dependencies:**
- `agents_final.py` - For routing and analysis
- `utils.py` - For data management

---

### **2. `agents_final.py` - AI Agent System**

**Purpose:** Core AI agent logic using PydanticAI and Gemini

**Key Components:**

#### **Master Agent**
- Routes user queries to appropriate specialist
- Analyzes query intent
- Returns: "diagnostic", "maintenance", or "performance"

#### **Diagnostic Agent**
- Analyzes vehicle health and detects issues
- Checks sensor readings against normal ranges
- Identifies anomalies, DTC codes, critical conditions
- **Tools:**
  - `get_vehicle_sensor_data()` - Fetch all sensor readings
  - `check_dtc_codes()` - Check diagnostic trouble codes

#### **Maintenance Agent**
- Provides maintenance recommendations
- Suggests service schedules
- Prioritizes by urgency (Immediate/Soon/Routine/Optional)
- **Tools:**
  - `get_vehicle_sensor_data()` - Fetch sensor data
  - `check_fluid_levels()` - Check oil, coolant, fuel, brake fluid

#### **Performance Agent**
- Analyzes vehicle performance metrics
- Evaluates efficiency and driving behavior
- Provides optimization recommendations
- **Tools:**
  - `get_vehicle_sensor_data()` - Fetch sensor data
  - `calculate_efficiency_metrics()` - Calculate RPM/speed ratios, thermal efficiency

**Key Functions:**
- `route_query()` - Routes query to appropriate agent
- `get_comprehensive_analysis()` - Runs all three agents in parallel

**Dependencies:**
- `utils.py` - VehicleDataManager, sensor ranges
- Google Gemini API (via PydanticAI)

---

### **3. `agents.py` - Legacy/Alternative Agent Implementations**

**Purpose:** Contains various agent implementations (not currently used by main.py)

**Contains:**
- `agent_ingestion()` - Data ingestion agent (for telemetry collection)
- `genai_data_analysis_agent()` - LLM-based anomaly detection
- `diagnosis_agent()` - ML + LLM diagnosis (TensorFlow, XGBoost)
- `manufacturing_insights_module()` - Manufacturing insights with PostgreSQL
- `feedback_agent()` - Feedback processing with Google Calendar & WhatsApp
- `bert_sentiment_agent()` - BERT sentiment analysis
- `quality_insights_agent()` - BigQuery & Tableau integration

**Note:** These appear to be alternative implementations or future features. The main system uses `agents_final.py`.

---

### **4. `utils.py` - Utility Functions & Data Management**

**Purpose:** Data management, sensor ranges, and logging utilities

**Key Classes:**

#### **VehicleDataManager**
- Manages vehicle data from JSON database
- **Methods:**
  - `get_vehicle_data(vehicle_id)` - Get complete vehicle record
  - `get_all_vehicles()` - Get all vehicles
  - `get_vehicle_ids()` - Get list of IDs
  - `get_sensor_data(vehicle_id, sensor_fields)` - Get specific sensors
  - `get_vehicle_type(vehicle_id)` - Get car type

#### **AnalysisLogger**
- In-memory logging of analysis results
- **Methods:**
  - `save_analysis(analysis_data)` - Log analysis entry
  - `get_vehicle_history(vehicle_id, limit)` - Get historical logs

#### **SENSOR_RANGES Dictionary**
- Defines normal/warning/critical ranges for sensors
- Used by agents to evaluate sensor health
- Includes: engine_temp_c, battery_voltage, oil_pressure_kpa, etc.

**Key Functions:**
- `get_sensor_status(sensor_name, value)` - Returns "normal"/"warning"/"critical"

---

### **5. `monitor_cron.py` - Scheduled Monitoring Service**

**Purpose:** Automated vehicle health monitoring (runs as cron job)

**Key Components:**

#### **MonitoringService Class**
- Performs scheduled health checks
- Detects critical issues
- Generates monitoring reports and alerts

**Key Methods:**
- `check_critical_sensors(vehicle_id)` - Check for critical sensor values
- `monitor_vehicle(vehicle_id)` - Monitor single vehicle
- `monitor_all_vehicles()` - Monitor all vehicles

**Output Files:**
- `dataset/monitoring_reports.json` - All monitoring reports
- `dataset/alerts.json` - Critical alerts only

**Usage:**
```bash
# Run manually
python monitor_cron.py

# Or set up cron job (runs hourly)
0 * * * * /usr/bin/python3 /path/to/monitor_cron.py
```

---

### **6. `dataset/vehicle_realtime_data.json` - Vehicle Database**

**Purpose:** JSON database containing vehicle sensor data

**Structure:**
```json
{
  "vehicles": [
    {
      "vehicle_id": "VH001",
      "car_type": "sedan_petrol",
      "available_sensor_fields": {
        "engine_temp_c": 92.5,
        "rpm": 1100,
        "battery_voltage": 12.4,
        ...
      }
    }
  ]
}
```

**Vehicle Types Supported:**
- sedan_petrol, electric_suv, diesel_truck, sports_car, hybrid_sedan
- delivery_van, tractor, electric_bus, scooter_petrol, luxury_sedan

**Sensor Fields Include:**
- Engine: engine_temp_c, rpm, oil_pressure_kpa, coolant_temp_c
- Battery: battery_voltage, battery_soc (for EVs)
- Fuel: fuel_level_percent
- Tires: tire_pressure_fl, tire_pressure_fr, tire_pressure_rl, tire_pressure_rr
- Location: gps_lat, gps_lon
- Diagnostics: dtc_codes (Diagnostic Trouble Codes)
- EV-specific: motor_temp_c, inverter_temp_c, charger_state
- Other: speed_kmph, ambient_temp_c, brake_fluid_level_percent

---

### **7. `requirements.txt` - Python Dependencies**

**Dependencies:**
- `fastapi==0.115.5` - Web framework
- `uvicorn[standard]==0.32.1` - ASGI server
- `pydantic==2.10.3` - Data validation
- `pydantic-ai==0.0.14` - AI agent framework
- `google-generativeai==0.8.3` - Gemini API client
- `python-dotenv==1.0.1` - Environment variable management

---

### **8. `vercel.json` - Deployment Configuration**

**Purpose:** Vercel serverless deployment configuration

**Configuration:**
- Uses `@vercel/python` builder
- Routes all requests to `main.py`
- Enables serverless function deployment

---

### **9. `README.md` - Project Documentation**

**Contains:**
- Project overview and features
- Installation instructions
- API endpoint documentation
- Usage examples
- Deployment guide

---

## 📊 Input/Output Schemas

### **API Request Schemas**

#### **1. Query Request** (`POST /query`)
```json
{
  "vehicle_id": "VH001",
  "query": "Is my car healthy?"
}
```

#### **2. Comprehensive Analysis Request** (`POST /analyze`)
```json
{
  "vehicle_id": "VH001"
}
```

---

### **API Response Schemas**

#### **1. Query Response** (`POST /query`)
```json
{
  "vehicle_id": "VH001",
  "agent_used": "diagnostic",
  "response": "Vehicle operating within safe limits. Engine temperature is normal at 92.5°C...",
  "timestamp": "2025-01-01T10:15:00"
}
```

#### **2. Comprehensive Analysis Response** (`POST /analyze`)
```json
{
  "vehicle_id": "VH001",
  "timestamp": "2025-01-01T10:15:00",
  "analysis": {
    "diagnostic": {
      "status": "success",
      "output": "Overall health status: Good. Engine temperature normal..."
    },
    "maintenance": {
      "status": "success",
      "output": "Recommended maintenance: Oil change due in 2,000 km..."
    },
    "performance": {
      "status": "success",
      "output": "Performance rating: Good. RPM to speed ratio indicates..."
    }
  }
}
```

#### **3. Vehicle Data Response** (`GET /vehicle/{vehicle_id}`)
```json
{
  "vehicle_id": "VH001",
  "car_type": "sedan_petrol",
  "available_sensor_fields": {
    "engine_temp_c": 92.5,
    "rpm": 1100,
    "battery_voltage": 12.4,
    "oil_pressure_kpa": 260,
    "coolant_temp_c": 89.3,
    "fuel_level_percent": 56.0,
    "speed_kmph": 0,
    "gps_lat": 28.6139,
    "gps_lon": 77.2090,
    "dtc_codes": ["P0420"],
    "tire_pressure_fl": 32.1,
    "tire_pressure_fr": 32.4,
    "tire_pressure_rl": 34.0,
    "tire_pressure_rr": 33.7,
    "brake_fluid_level_percent": 78.0
  }
}
```

#### **4. Vehicle List Response** (`GET /vehicles`)
```json
{
  "vehicles": ["VH001", "VH002", "VH003", ...],
  "total": 10
}
```

#### **5. History Response** (`GET /history/{vehicle_id}`)
```json
{
  "vehicle_id": "VH001",
  "total_entries": 5,
  "history": [
    {
      "timestamp": "2025-01-01T10:15:00",
      "vehicle_id": "VH001",
      "query": "Is my car healthy?",
      "agent": "diagnostic",
      "response": "Vehicle operating within safe limits..."
    },
    ...
  ]
}
```

---

## 🤖 Agent System Details

### **Master Agent Routing Logic**

The Master Agent analyzes user queries and routes to:

1. **Diagnostic Agent** - For:
   - Health checks ("Is my car healthy?")
   - Error codes ("Check engine light is on")
   - Troubleshooting ("What's wrong?")
   - System diagnostics

2. **Maintenance Agent** - For:
   - Service recommendations ("What maintenance is needed?")
   - Maintenance schedules ("When should I service?")
   - Fluid checks ("Check oil level")
   - Preventive care

3. **Performance Agent** - For:
   - Performance metrics ("How is my car performing?")
   - Fuel efficiency ("What's my fuel economy?")
   - Optimization ("How can I improve efficiency?")
   - Driving behavior analysis

### **Agent Tool System**

Each specialized agent has access to tools:

**Diagnostic Agent Tools:**
- `get_vehicle_sensor_data()` - Fetch all sensors
- `check_dtc_codes()` - Check error codes

**Maintenance Agent Tools:**
- `get_vehicle_sensor_data()` - Fetch sensors
- `check_fluid_levels()` - Check fluids (oil, coolant, fuel, brake)

**Performance Agent Tools:**
- `get_vehicle_sensor_data()` - Fetch sensors
- `calculate_efficiency_metrics()` - Calculate efficiency ratios

---

## 🌐 API Endpoints Reference

### **Core Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information |
| `GET` | `/health` | Health check + vehicle count |
| `GET` | `/vehicles` | List all vehicle IDs |
| `GET` | `/vehicle/{vehicle_id}` | Get complete vehicle data |
| `GET` | `/history/{vehicle_id}?limit=10` | Get analysis history |

### **AI-Powered Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/query` | Ask question about vehicle (routed to appropriate agent) |
| `POST` | `/analyze` | Get comprehensive analysis from all agents |

---

## 📦 Data Structures

### **Vehicle Data Structure**
```python
{
  "vehicle_id": str,           # e.g., "VH001"
  "car_type": str,             # e.g., "sedan_petrol", "electric_suv"
  "available_sensor_fields": {
    "engine_temp_c": float,
    "rpm": int,
    "battery_voltage": float,
    "oil_pressure_kpa": float,
    "coolant_temp_c": float,
    "fuel_level_percent": float,
    "speed_kmph": float,
    "gps_lat": float,
    "gps_lon": float,
    "dtc_codes": List[str],
    "tire_pressure_fl": float,
    "tire_pressure_fr": float,
    "tire_pressure_rl": float,
    "tire_pressure_rr": float,
    "brake_fluid_level_percent": float,
    # EV-specific:
    "battery_soc": int,        # State of Charge %
    "motor_temp_c": float,
    "inverter_temp_c": float,
    "charger_state": str,
    # Other:
    "ambient_temp_c": float,
    "cabin_temp_c": float,
    "brake_temp_fl_c": float,
    "load_weight_kg": float,
    "passenger_count": int
  }
}
```

### **Sensor Range Structure** (from `SENSOR_RANGES`)
```python
{
  "sensor_name": {
    "normal": (min, max),
    "warning": (min, max),
    "critical": (min, max),
    "description": str
  }
}
```

### **Analysis Log Entry**
```python
{
  "timestamp": str,            # ISO format
  "vehicle_id": str,
  "query": str,                # User query (for /query endpoint)
  "agent": str,                # "diagnostic", "maintenance", or "performance"
  "response": str,             # Agent's response
  # OR for comprehensive analysis:
  "type": "comprehensive_analysis",
  "result": {
    "diagnostic": {...},
    "maintenance": {...},
    "performance": {...}
  }
}
```

---

## 🔧 Environment Variables

**Required:**
- `GEMINI_API_KEY` - Google Gemini API key for LLM access

**Setup:**
```bash
# Linux/macOS
export GEMINI_API_KEY='your-api-key-here'

# Windows PowerShell
$env:GEMINI_API_KEY = 'your-api-key-here'
```

---

## 🚀 Running the System

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Set Environment Variable**
```bash
export GEMINI_API_KEY='your-api-key'
```

### **3. Start Server**
```bash
python main.py
```

### **4. Access API**
- API: `http://localhost:8000`
- Interactive Docs: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

### **5. Run Monitoring (Optional)**
```bash
python monitor_cron.py
```

---

## 📈 Key Features

1. **Intelligent Query Routing** - Master Agent routes queries to the right specialist
2. **Parallel Analysis** - Comprehensive analysis runs all agents simultaneously
3. **Tool-Based Agents** - Agents use tools to fetch and analyze data
4. **Historical Logging** - All analyses are logged for review
5. **Automated Monitoring** - Cron job for scheduled health checks
6. **Multi-Vehicle Support** - Handles multiple vehicle types (petrol, electric, hybrid, etc.)
7. **Sensor Range Validation** - Built-in sensor health evaluation
8. **Error Handling** - Graceful error handling with fallbacks

---

## 🔮 Future Enhancements (from README)

- Persistent database (PostgreSQL / MongoDB)
- Real-time telemetry ingestion
- Alerting & notification system
- Agent memory and learning loop
- Dashboard frontend (React)
- Mobile application (React Native)
- OEM & IoT integrations

---

## 📝 Summary

This is a **production-ready AI agent system** for vehicle analysis that:
- Uses **FastAPI** for the web API
- Implements **agentic AI** with specialized agents
- Routes queries intelligently via a **Master Agent**
- Provides **diagnostic, maintenance, and performance** insights
- Supports **multiple vehicle types** (petrol, electric, hybrid, etc.)
- Includes **automated monitoring** capabilities
- Uses **LLM-powered analysis** with Google Gemini
- Stores data in **JSON files** (easily extensible to databases)

The system is designed to be **modular, scalable, and production-ready** while demonstrating modern AI agent architecture patterns.

