"""
Specialized AI Agents for Vehicle Analysis using PydanticAI
Filename: agents_final.py
"""
import os
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pydantic import BaseModel, Field
import json

# Third-party imports
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

# Local imports (ensure utils.py exists in the same directory)
from utils import VehicleDataManager, get_sensor_status, SENSOR_RANGES

# Load environment variables (optional, since we are hardcoding the key below)
load_dotenv()

# ============================================================================
# RESPONSE MODELS FOR STRUCTURED OUTPUT
# ============================================================================

class DiagnosticResponse(BaseModel):
    """Structured diagnostic analysis output"""
    rca: str = Field(description="Root cause analysis of the issue")
    priority: str = Field(description="Priority level: HIGH, MEDIUM, or LOW")
    repair_timeline: str = Field(description="Repair timeline in days, e.g., 'Within 2 days'")
    failure_probability: str = Field(description="Failure probability percentage, e.g., '85%'")


class MaintenanceResponse(BaseModel):
    """Structured maintenance analysis output"""
    rca: str = Field(description="Maintenance need analysis")
    priority: str = Field(description="Priority level: HIGH, MEDIUM, or LOW")
    repair_timeline: str = Field(description="Maintenance timeline in days")
    failure_probability: str = Field(description="Failure probability if not maintained")


class PerformanceResponse(BaseModel):
    """Structured performance analysis output"""
    rca: str = Field(description="Performance degradation analysis")
    priority: str = Field(description="Priority level: HIGH, MEDIUM, or LOW")
    repair_timeline: str = Field(description="Optimization timeline in days")
    failure_probability: str = Field(description="Complete performance failure probability")

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

# Configuration for the AI Model — use Groq exclusively
# The `openai` client library is used to talk to Groq's OpenAI-compatible API.
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_BASE = "https://api.groq.com/openai/v1"

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY not set. Agent functionality will be limited.")
    print("Set GROQ_API_KEY environment variable for full functionality.")

# Use Groq model. pydantic_ai's OpenAIModel can point at Groq's OpenAI-compatible endpoint.
active_model = OpenAIModel(
    model_name="openai/gpt-oss-20b",
    base_url=GROQ_BASE,
    api_key=GROQ_API_KEY or "dummy-key-for-startup"  # Dummy key to prevent startup crash
)

@dataclass
class VehicleContext:
    """Context passed to agents"""
    vehicle_id: str
    data_manager: VehicleDataManager
    processed_packets: Optional[list] = None  # Pre-processed data from startup
    anomalies: Optional[Dict] = None  # Detected anomalies
    analysis_info: Optional[str] = None  # Additional analysis metadata


# ============================================================================
# 1. DIAGNOSTIC AGENT
# ============================================================================

diagnostic_agent = Agent(
    active_model,
    result_type=DiagnosticResponse,
    deps_type=VehicleContext,
    system_prompt="""You are an expert automotive diagnostic AI. Analyze sensor data and return ONLY structured JSON.

Analyze all sensor categories: battery, motor, brakes, chassis, electrical/ECU, DTC codes, component aging, rate of change, signal consistency, operational context.

Return ONLY these fields:
- rca: Root cause analysis (concise, data-driven)
- priority: HIGH (safety-critical, 1-2 days) | MEDIUM (performance issue, 3-7 days) | LOW (minor, 7-30 days)
- repair_timeline: "Within X days" or "Immediate"
- failure_probability: "X%" (0-100%, based on sensor data, DTC codes, component age)

Be concise. Reference specific sensor values."""
)


@diagnostic_agent.tool
async def get_vehicle_sensor_data(ctx: RunContext[VehicleContext]) -> Dict[str, Any]:
    """
    Fetch all sensor data for the vehicle being diagnosed.
    Returns complete sensor readings.
    """
    vehicle_data = ctx.deps.data_manager.get_vehicle_data(ctx.deps.vehicle_id)
    if not vehicle_data:
        return {"error": "Vehicle not found"}
    
    out = {
        "vehicle_id": vehicle_data.get("vehicle_id"),
        "car_type": vehicle_data.get("car_type"),
        "timestamp_utc": vehicle_data.get("timestamp_utc"),
        "sensors": vehicle_data.get("available_sensor_fields", {})
    }
    if vehicle_data.get("raw_sensor_categories"):
        out["raw_sensor_categories"] = vehicle_data["raw_sensor_categories"]
    return out


@diagnostic_agent.tool
async def check_dtc_codes(ctx: RunContext[VehicleContext]) -> Dict[str, Any]:
    """
    Check for Diagnostic Trouble Codes (DTCs) and fault codes in the vehicle.
    """
    vehicle_data = ctx.deps.data_manager.get_vehicle_data(ctx.deps.vehicle_id)
    if not vehicle_data:
        return {"dtc_codes": [], "fault_code_count": 0}
    
    sensors = vehicle_data.get("available_sensor_fields", {})
    raw = vehicle_data.get("raw_sensor_categories", {})
    dtc_codes = sensors.get("dtc_codes", [])
    
    if raw and "electrical_ecu" in raw:
        ecu = raw["electrical_ecu"]
        fault_count = ecu.get("fault_code_active_count", 0)
        can_errors = ecu.get("can_bus_error_count", 0)
        dropouts = ecu.get("sensor_signal_dropouts", 0)
        return {
            "dtc_codes": dtc_codes,
            "fault_code_active_count": fault_count,
            "can_bus_error_count": can_errors,
            "sensor_signal_dropouts": dropouts,
            "electrical_ecu_status": "issues detected" if (fault_count or can_errors or dropouts) else "clean"
        }
    
    # Fallback for mock data if raw categories missing
    dtc_meanings = {
        "P0420": "Catalyst system efficiency below threshold",
        "P0301": "Cylinder 1 misfire detected",
        "P0171": "System too lean",
        "P0300": "Random/multiple cylinder misfire"
    }
    return {
        "dtc_codes": dtc_codes,
        "meanings": {code: dtc_meanings.get(code, "Unknown code") for code in dtc_codes}
    }


# ============================================================================
# 2. MAINTENANCE AGENT
# ============================================================================

maintenance_agent = Agent(
    active_model,
    result_type=MaintenanceResponse,
    deps_type=VehicleContext,
    system_prompt="""You are an expert automotive maintenance AI. Analyze maintenance needs and return ONLY structured JSON.

Analyze: battery system, brake system, motor/inverter, electrical/ECU, chassis/suspension, component aging, operational context.

Return ONLY these fields:
- rca: Maintenance need analysis (concise, specific component and reason)
- priority: HIGH (safety-critical, 1-2 days) | MEDIUM (performance-affecting, 7-14 days) | LOW (preventive, 30-60 days)
- repair_timeline: "Within X days"
- failure_probability: "X%" (probability of component failure if not maintained)

Be specific about which component needs maintenance."""
)


@maintenance_agent.tool
async def get_vehicle_sensor_data(ctx: RunContext[VehicleContext]) -> Dict[str, Any]:
    """
    Fetch all sensor data for maintenance analysis.
    """
    vehicle_data = ctx.deps.data_manager.get_vehicle_data(ctx.deps.vehicle_id)
    if not vehicle_data:
        return {"error": "Vehicle not found"}
    
    out = {
        "vehicle_id": vehicle_data.get("vehicle_id"),
        "car_type": vehicle_data.get("car_type"),
        "timestamp_utc": vehicle_data.get("timestamp_utc"),
        "sensors": vehicle_data.get("available_sensor_fields", {})
    }
    if vehicle_data.get("raw_sensor_categories"):
        out["raw_sensor_categories"] = vehicle_data["raw_sensor_categories"]
    return out


@maintenance_agent.tool
async def check_fluid_levels(ctx: RunContext[VehicleContext]) -> Dict[str, str]:
    """
    Check fluid/systems status: oil, coolant, brake fluid, fuel, battery coolant.
    """
    sensors = ctx.deps.data_manager.get_sensor_data(ctx.deps.vehicle_id)
    raw = ctx.deps.data_manager.get_raw_categories(ctx.deps.vehicle_id)
    fluid_status = {}
    
    if "fuel_level_percent" in sensors:
        fuel = sensors["fuel_level_percent"]
        if isinstance(fuel, (int, float)):
            fluid_status["fuel"] = "critical - refuel immediately" if fuel < 10 else ("low - refuel soon" if fuel < 25 else "normal")
    
    if "brake_fluid_level_percent" in sensors:
        brake = sensors["brake_fluid_level_percent"]
        if isinstance(brake, (int, float)):
            fluid_status["brake_fluid"] = "critical - safety issue" if brake < 50 else ("low - top up" if brake < 70 else "normal")
    
    if "oil_pressure_kpa" in sensors:
        oil = sensors["oil_pressure_kpa"]
        if isinstance(oil, (int, float)):
            fluid_status["oil"] = "critical - low pressure" if oil < 150 else ("low - check level" if oil < 200 else "normal")
    
    if raw and "brake_sensors" in raw:
        b = raw["brake_sensors"]
        hydraulic = b.get("hydraulic_brake_pressure_bar")
        if isinstance(hydraulic, (int, float)):
            fluid_status["brake_hydraulic_pressure"] = "normal" if 50 < hydraulic < 150 else ("warning" if hydraulic < 50 or hydraulic > 180 else "check")
    
    if raw and "battery_sensors" in raw:
        soc = raw["battery_sensors"].get("battery_soc_pct")
        soh = raw["battery_sensors"].get("battery_soh_pct")
        if isinstance(soc, (int, float)):
            fluid_status["battery_soc"] = "critical" if soc < 10 else ("low" if soc < 20 else "normal")
        if isinstance(soh, (int, float)):
            fluid_status["battery_soh"] = "degraded" if soh < 80 else "healthy"
    
    return fluid_status


# ============================================================================
# 3. PERFORMANCE AGENT
# ============================================================================

performance_agent = Agent(
    active_model,
    result_type=PerformanceResponse,
    deps_type=VehicleContext,
    system_prompt="""You are an expert automotive performance AI. Analyze performance issues and return ONLY structured JSON.

Analyze: vehicle motion, idle usage, energy usage, battery/motor, rate of change, signal consistency, operational context.

Return ONLY these fields:
- rca: Performance degradation analysis (concise, identify cause and impact)
- priority: HIGH (severe loss, safety concern, 1-3 days) | MEDIUM (noticeable degradation, 7-14 days) | LOW (minor, 30+ days)
- repair_timeline: "Within X days"
- failure_probability: "X%" (probability of complete performance failure)

Focus on actionable performance issues."""
)


@performance_agent.tool
async def get_vehicle_sensor_data(ctx: RunContext[VehicleContext]) -> Dict[str, Any]:
    """
    Fetch all sensor data for performance analysis.
    """
    vehicle_data = ctx.deps.data_manager.get_vehicle_data(ctx.deps.vehicle_id)
    if not vehicle_data:
        return {"error": "Vehicle not found"}
    
    out = {
        "vehicle_id": vehicle_data.get("vehicle_id"),
        "car_type": vehicle_data.get("car_type"),
        "timestamp_utc": vehicle_data.get("timestamp_utc"),
        "sensors": vehicle_data.get("available_sensor_fields", {})
    }
    if vehicle_data.get("raw_sensor_categories"):
        out["raw_sensor_categories"] = vehicle_data["raw_sensor_categories"]
    return out


@performance_agent.tool
async def calculate_efficiency_metrics(ctx: RunContext[VehicleContext]) -> Dict[str, Any]:
    """
    Calculate efficiency metrics.
    """
    sensors = ctx.deps.data_manager.get_sensor_data(ctx.deps.vehicle_id)
    raw = ctx.deps.data_manager.get_raw_categories(ctx.deps.vehicle_id)
    metrics = {}
    
    if raw:
        eu = raw.get("energy_usage", {})
        iu = raw.get("idle_usage", {})
        bs = raw.get("battery_sensors", {})
        vm = raw.get("vehicle_motion", {})
        if eu:
            metrics["energy_consumption_kwh_per_km"] = eu.get("energy_consumption_kwh_per_km")
            metrics["driving_efficiency_score"] = eu.get("driving_efficiency_score")
            metrics["regen_braking_contribution_pct"] = eu.get("regen_braking_contribution_pct")
            metrics["idle_energy_wastage_kwh"] = eu.get("idle_energy_wastage_kwh")
            metrics["efficiency_degradation_trend"] = eu.get("efficiency_degradation_trend")
        if iu:
            metrics["idle_to_drive_ratio"] = iu.get("idle_to_drive_ratio")
            metrics["idling_time_min"] = iu.get("idling_time_min")
        if bs:
            metrics["battery_soc_pct"] = bs.get("battery_soc_pct")
            metrics["battery_soh_pct"] = bs.get("battery_soh_pct")
        if vm:
            metrics["speed_stability_score"] = vm.get("speed_stability_score")
            metrics["avg_speed_per_trip_kmph"] = vm.get("avg_speed_per_trip_kmph")
    
    if "rpm" in sensors and "speed_kmph" in sensors:
        rpm, speed = sensors["rpm"], sensors["speed_kmph"]
        if isinstance(rpm, (int, float)) and isinstance(speed, (int, float)) and speed > 0:
            metrics["rpm_per_kmph"] = round(rpm / speed, 2)
    
    if "battery_soc" in sensors or "battery_sensors_battery_soc_pct" in sensors:
        soc = sensors.get("battery_soc") or sensors.get("battery_sensors_battery_soc_pct")
        if isinstance(soc, (int, float)):
            metrics["battery_level"] = f"{soc}%"
            if soc < 20:
                metrics["range_concern"] = "low battery - charge soon"
    
    if "engine_temp_c" in sensors or "motor_inverter_sensors_inverter_temperature_c" in sensors:
        temp = sensors.get("engine_temp_c") or sensors.get("motor_inverter_sensors_inverter_temperature_c")
        if isinstance(temp, (int, float)):
            metrics["thermal_status"] = "optimal" if 80 <= temp <= 95 else ("cool" if temp < 80 else "running hot")
    
    return metrics


# ============================================================================
# 4. MASTER AGENT & ROUTING
# ============================================================================

master_agent = Agent(
    active_model,
    system_prompt="""You are the master vehicle analysis coordinator AI.

Your role is to understand user queries about their vehicle and route them to the appropriate specialist:

1. DIAGNOSTIC AGENT - For questions about:
   - Current vehicle health and status
   - Warning lights or error codes
   - Strange noises or behaviors
   - "What's wrong with my car?"
   - System diagnostics and troubleshooting

2. MAINTENANCE AGENT - For questions about:
   - Service recommendations
   - Maintenance schedules
   - Fluid changes and checks
   - "When should I service my car?"
   - Preventive maintenance advice

3. PERFORMANCE AGENT - For questions about:
   - Vehicle performance and efficiency
   - Fuel economy or range
   - Driving optimization
   - "How is my car performing?"
   - Performance metrics and analysis

Analyze the user's query and respond with ONLY ONE of these exact words:
- "diagnostic"
- "maintenance"
- "performance"

If the query is unclear or could apply to multiple agents, choose the most relevant one."""
)


async def route_query(query: str, vehicle_id: str, data_manager: VehicleDataManager, analysis_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Route user query to appropriate agent and get response.
    Uses pre-processed buffer if analysis_context is provided.
    """
    # First, use master agent to determine routing
    routing_result = await master_agent.run(query)
    agent_type = routing_result.data.strip().lower()
    
    # Create context for the specialized agent
    context = VehicleContext(vehicle_id=vehicle_id, data_manager=data_manager)
    
    # Add analysis context if provided
    if analysis_context:
        context.processed_packets = analysis_context.get("processed_packets", [])
        context.anomalies = analysis_context.get("anomalies_detected", {})
        context.analysis_info = f"Pre-processed {analysis_context.get('total_packets', 0)} packets with {analysis_context.get('total_anomalies', 0)} anomalies detected"
    
    # Route to appropriate agent
    if agent_type == "diagnostic":
        result = await diagnostic_agent.run(
            f"Analyze the vehicle and respond to: {query}",
            deps=context
        )
        return {
            "agent": "diagnostic",
            "rca": result.data.rca,
            "priority": result.data.priority,
            "repair_timeline": result.data.repair_timeline,
            "failure_probability": result.data.failure_probability,
            "vehicle_id": vehicle_id
        }
    
    elif agent_type == "maintenance":
        result = await maintenance_agent.run(
            f"Provide maintenance guidance for: {query}",
            deps=context
        )
        return {
            "agent": "maintenance",
            "rca": result.data.rca,
            "priority": result.data.priority,
            "repair_timeline": result.data.repair_timeline,
            "failure_probability": result.data.failure_probability,
            "vehicle_id": vehicle_id
        }
    
    elif agent_type == "performance":
        result = await performance_agent.run(
            f"Analyze performance regarding: {query}",
            deps=context
        )
        return {
            "agent": "performance",
            "rca": result.data.rca,
            "priority": result.data.priority,
            "repair_timeline": result.data.repair_timeline,
            "failure_probability": result.data.failure_probability,
            "vehicle_id": vehicle_id
        }
    
    else:
        # Default to diagnostic if routing unclear
        result = await diagnostic_agent.run(
            f"Analyze the vehicle and respond to: {query}",
            deps=context
        )
        return {
            "agent": "diagnostic",
            "rca": result.data.rca,
            "priority": result.data.priority,
            "repair_timeline": result.data.repair_timeline,
            "failure_probability": result.data.failure_probability,
            "vehicle_id": vehicle_id
        }


async def get_comprehensive_analysis(vehicle_id: str, data_manager: VehicleDataManager, analysis_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Runs all agents in parallel for a full report.
    Uses pre-processed buffer if analysis_context is provided.
    """
    context = VehicleContext(vehicle_id=vehicle_id, data_manager=data_manager)
    
    # Add analysis context if provided
    if analysis_context:
        context.processed_packets = analysis_context.get("processed_packets", [])
        context.anomalies = analysis_context.get("anomalies_detected", {})
        context.analysis_info = f"Pre-processed {analysis_context.get('total_packets', 0)} packets with {analysis_context.get('total_anomalies', 0)} anomalies detected"

    try:
        diagnostic_task = diagnostic_agent.run(
            "Perform complete diagnostic analysis of this vehicle. Check all systems and sensors.",
            deps=context
        )

        maintenance_task = maintenance_agent.run(
            "Provide complete maintenance assessment and recommendations for this vehicle.",
            deps=context
        )

        performance_task = performance_agent.run(
            "Analyze overall performance, efficiency, and driving metrics for this vehicle.",
            deps=context
        )

        # Run all concurrently
        diagnostic_result, maintenance_result, performance_result = await asyncio.gather(
            diagnostic_task,
            maintenance_task,
            performance_task,
            return_exceptions=True 
        )

        def safe_data(result, name):
            if isinstance(result, Exception):
                return {
                    "status": "failed",
                    "agent": name,
                    "error": repr(result)
                }
            # Extract structured data from BaseModel
            return {
                "status": "success",
                "rca": result.data.rca,
                "priority": result.data.priority,
                "repair_timeline": result.data.repair_timeline,
                "failure_probability": result.data.failure_probability
            }

        return {
            "vehicle_id": vehicle_id,
            "diagnostic": safe_data(diagnostic_result, "diagnostic"),
            "maintenance": safe_data(maintenance_result, "maintenance"),
            "performance": safe_data(performance_result, "performance"),
        }

    except Exception as e:
        print("[FATAL ANALYSIS ERROR]", repr(e))
        raise