"""
Utility functions for vehicle data management
"""
import json
from typing import Dict, List, Optional, Any
from pathlib import Path


def _flatten_dict(d: Dict, parent_key: str = "", sep: str = "_") -> Dict[str, Any]:
    """Flatten nested dict to keys like 'battery_sensors_battery_soc_pct' for compatibility."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict) and v:
            items.extend(_flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def _transform_newdata_record(record: Dict, vehicle_id: str = "default") -> Dict:
    """Transform newData.json record into vehicle-like structure for agents."""
    raw = {k: v for k, v in record.items() if k != "vehicle"}
    timestamp = record.get("vehicle", {}).get("timestamp_utc", "")
    flattened = _flatten_dict(raw)
    return {
        "vehicle_id": vehicle_id,
        "car_type": "electric_vehicle",
        "timestamp_utc": timestamp,
        "available_sensor_fields": flattened,
        "raw_sensor_categories": raw,
    }


class VehicleDataManager:
    """Manages vehicle data from JSON database (supports oldData and newData formats)"""
    
    def __init__(self, db_path: str = "dataset/newData.json"):
        self.db_path = Path(db_path)
        self.data = self._load_data()
        self._is_new_format = self._detect_format()
    
    def _detect_format(self) -> bool:
        """Detect if data is newData (array) or oldData (vehicles object) format."""
        if isinstance(self.data, list):
            return True
        if isinstance(self.data, dict) and "vehicles" in self.data:
            return False
        return False
    
    def _load_data(self) -> Any:
        """Load vehicle data from JSON file"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"vehicles": []}
    
    def get_vehicle_data(self, vehicle_id: str, snapshot_index: Optional[int] = None) -> Optional[Dict]:
        """
        Fetch data for a specific vehicle by ID.
        
        For newData format: vehicle_id can be "default" or "VH001"; returns latest snapshot by default.
        For oldData format: returns vehicle by vehicle_id from vehicles array.
        
        Args:
            vehicle_id: Vehicle identifier (e.g., "VH001" or "default")
            snapshot_index: For newData only - specific record index. None = latest.
        
        Returns:
            Dictionary containing vehicle data or None if not found
        """
        if self._is_new_format:
            records = self.data
            if not records:
                return None
            idx = snapshot_index if snapshot_index is not None else -1
            record = records[idx]
            return _transform_newdata_record(record, vehicle_id)
        
        for vehicle in self.data.get("vehicles", []):
            if vehicle.get("vehicle_id") == vehicle_id:
                return vehicle
        return None
    
    def get_all_vehicles(self) -> List[Dict]:
        """Get data for all vehicles"""
        if self._is_new_format:
            return [self.get_vehicle_data("default")]
        return self.data.get("vehicles", [])
    
    def get_vehicle_ids(self) -> List[str]:
        """Get list of all vehicle IDs"""
        if self._is_new_format:
            return ["default"]
        return [v.get("vehicle_id") for v in self.data.get("vehicles", [])]
    
    def get_sensor_data(self, vehicle_id: str, sensor_fields: Optional[List[str]] = None) -> Dict:
        """
        Get specific sensor data from a vehicle.
        For newData: returns flattened sensors. Use get_vehicle_data() for raw_sensor_categories.
        
        Args:
            vehicle_id: Vehicle identifier
            sensor_fields: List of sensor field names to fetch. If None, returns all.
        
        Returns:
            Dictionary of sensor readings
        """
        vehicle = self.get_vehicle_data(vehicle_id)
        if not vehicle:
            return {}
        
        sensors = vehicle.get("available_sensor_fields", {})
        
        if sensor_fields is None:
            return sensors
        
        return {field: sensors.get(field) for field in sensor_fields if field in sensors}
    
    def get_vehicle_type(self, vehicle_id: str) -> Optional[str]:
        """Get vehicle type/category"""
        vehicle = self.get_vehicle_data(vehicle_id)
        return vehicle.get("car_type") if vehicle else None
    
    def get_raw_categories(self, vehicle_id: str) -> Optional[Dict]:
        """For newData format: return full nested sensor categories for detailed analysis."""
        vehicle = self.get_vehicle_data(vehicle_id)
        return vehicle.get("raw_sensor_categories") if vehicle else None
    
    def get_snapshot_count(self) -> int:
        """For newData format: total number of telemetry snapshots."""
        if self._is_new_format:
            return len(self.data)
        return 0


class AnalysisLogger:
    def __init__(self):
        self.logs = []

    def save_analysis(self, analysis_data: Dict) -> None:
        self.logs.append(analysis_data)

        if len(self.logs) > 1000:
            self.logs = self.logs[-1000:]

    def get_vehicle_history(self, vehicle_id: str, limit: int = 10):
        vehicle_logs = [
            log for log in self.logs
            if log.get("vehicle_id") == vehicle_id
        ]
        return vehicle_logs[-limit:]


# Sensor value reference ranges and descriptions (oldData + newData fields)
SENSOR_RANGES = {
    # Legacy / oldData
    "engine_temp_c": {"normal": (85, 105), "warning": (105, 110), "critical": (110, float('inf')), "description": "Engine temperature °C."},
    "battery_voltage": {"normal": (12.4, 14.8), "warning": (12.0, 12.4), "critical": (0, 12.0), "description": "12V battery. EV pack: 300-450V."},
    "battery_soc": {"normal": (20, 100), "warning": (10, 20), "critical": (0, 10), "description": "Battery State of Charge %."},
    "oil_pressure_kpa": {"normal": (200, 350), "warning": (150, 200), "critical": (0, 150), "description": "Oil pressure kPa."},
    "coolant_temp_c": {"normal": (80, 95), "warning": (95, 105), "critical": (105, float('inf')), "description": "Coolant temp °C."},
    "rpm": {"normal": (0, 3000), "warning": (3000, 5000), "critical": (5000, float('inf')), "description": "Engine RPM."},
    "fuel_level_percent": {"normal": (25, 100), "warning": (10, 25), "critical": (0, 10), "description": "Fuel level %."},
    "tire_pressure_fl": {"normal": (30, 35), "warning": (25, 30), "critical": (0, 25), "description": "Tire pressure PSI."},
    "motor_temp_c": {"normal": (40, 80), "warning": (80, 90), "critical": (90, float('inf')), "description": "Motor temp °C."},
    "brake_fluid_level_percent": {"normal": (70, 100), "warning": (50, 70), "critical": (0, 50), "description": "Brake fluid %."},
    # newData - battery_sensors
    "battery_sensors_battery_soc_pct": {"normal": (20, 100), "warning": (10, 20), "critical": (0, 10), "description": "Battery SOC %."},
    "battery_sensors_battery_soh_pct": {"normal": (80, 100), "warning": (70, 80), "critical": (0, 70), "description": "Battery State of Health %."},
    "battery_sensors_battery_pack_voltage_v": {"normal": (300, 450), "warning": (250, 300), "critical": (0, 250), "description": "Pack voltage V."},
    "battery_sensors_battery_temperature_avg_c": {"normal": (15, 45), "warning": (45, 55), "critical": (55, float('inf')), "description": "Battery avg temp °C."},
    "battery_sensors_battery_temperature_max_c": {"normal": (15, 50), "warning": (50, 60), "critical": (60, float('inf')), "description": "Battery max temp °C."},
    # newData - motor_inverter_sensors
    "motor_inverter_sensors_inverter_temperature_c": {"normal": (30, 70), "warning": (70, 85), "critical": (85, float('inf')), "description": "Inverter temp °C."},
    # newData - brake_sensors
    "brake_sensors_brake_disc_temperature_c": {"normal": (0, 150), "warning": (150, 250), "critical": (250, float('inf')), "description": "Brake disc temp °C."},
    "brake_sensors_brake_pad_wear_level_pct": {"normal": (50, 100), "warning": (25, 50), "critical": (0, 25), "description": "Brake pad life % remaining."},
    # newData - electrical_ecu
    "electrical_ecu_battery_12v_voltage": {"normal": (12.4, 14.8), "warning": (12.0, 12.4), "critical": (0, 12.0), "description": "12V auxiliary battery V."},
    "electrical_ecu_ecu_temperature_c": {"normal": (0, 60), "warning": (60, 75), "critical": (75, float('inf')), "description": "ECU temp °C."},
    "electrical_ecu_can_bus_error_count": {"normal": (0, 0), "warning": (1, 5), "critical": (5, float('inf')), "description": "CAN bus errors."},
    "electrical_ecu_fault_code_active_count": {"normal": (0, 0), "warning": (1, 3), "critical": (3, float('inf')), "description": "Active fault codes."},
    # newData - component_aging
    "component_aging_battery_capacity_fade_pct": {"normal": (0, 5), "warning": (5, 15), "critical": (15, float('inf')), "description": "Battery capacity fade %."},
    "component_aging_motor_efficiency_loss_pct": {"normal": (0, 5), "warning": (5, 15), "critical": (15, float('inf')), "description": "Motor efficiency loss %."},
    # newData - energy_usage
    "energy_usage_driving_efficiency_score": {"normal": (6, 10), "warning": (4, 6), "critical": (0, 4), "description": "Efficiency score 0-10."},
}


def get_sensor_status(sensor_name: str, value: float) -> str:
    """
    Determine sensor status based on value
    
    Returns: "normal", "warning", or "critical"
    """
    if sensor_name not in SENSOR_RANGES:
        return "normal"
    
    ranges = SENSOR_RANGES[sensor_name]
    
    if ranges["critical"][0] <= value <= ranges["critical"][1]:
        return "critical"
    elif ranges["warning"][0] <= value <= ranges["warning"][1]:
        return "warning"
    else:
        return "normal"
