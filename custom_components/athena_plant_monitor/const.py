"""Constants for the Athena Plant Monitor integration."""

DOMAIN = "athena_plant_monitor"

# Platforms
PLATFORMS = [
    "sensor",
    "binary_sensor", 
    "switch",
    "number",
    "select",
    "button",
]

# Configuration
CONF_DEVICE_ID = "device_id"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_GROWTH_PHASE = "growth_phase"
CONF_CROP_STEERING = "crop_steering"
CONF_SUBSTRATE_SIZE = "substrate_size"
CONF_VWC_TARGET = "vwc_target"
CONF_EC_TARGET = "ec_target"
CONF_PH_TARGET = "ph_target"
CONF_VPD_TARGET = "vpd_target"

# Configuration Keys für externe Entitäten
CONF_EXTERNAL_LIGHT_ENTITY = "external_light_entity"
CONF_LIGHT_SCHEDULE_START = "light_schedule_start"
CONF_LIGHT_SCHEDULE_END = "light_schedule_end"

# Defaults
DEFAULT_UPDATE_INTERVAL = 30  # seconds
DEFAULT_SUBSTRATE_SIZE = 10.0  # liters
DEFAULT_VWC_TARGET = 75.0  # percent
DEFAULT_EC_TARGET = 4.0  # ppm
DEFAULT_PH_TARGET = 6.0
DEFAULT_VPD_TARGET = 1.0  # kPa
DEFAULT_LIGHT_SCHEDULE_START = "06:00"
DEFAULT_LIGHT_SCHEDULE_END = "22:00"

# Data storage
DATA_COORDINATOR = "coordinator"
DATA_CONFIG = "config"

# ESPHome Entity IDs
ESPHOME_ENTITIES = {
    # Indoor sensors
    "temperature": "sensor.{device_id}_temperature",
    "humidity": "sensor.{device_id}_humidity", 
    "pressure": "sensor.{device_id}_pressure",
    "vwc": "sensor.{device_id}_vwc",
    "ec_substrate": "sensor.{device_id}_ec_substrate",
    "ph_substrate": "sensor.{device_id}_ph_substrate",
    "temp_substrate": "sensor.{device_id}_temp_substrate",
    "co2": "sensor.{device_id}_co2",
    "water_level": "sensor.{device_id}_water_level",
    
    # Actuators (ESPHome)
    "pump": "switch.{device_id}_pump",
    "fan_intake": "switch.{device_id}_fan_intake",
    "fan_exhaust": "switch.{device_id}_fan_exhaust",
    "humidifier": "switch.{device_id}_humidifier",
    "dehumidifier": "switch.{device_id}_dehumidifier",
    "co2_valve": "switch.{device_id}_co2_valve",
    
    # Light Control (kann ESPHome oder externe Switch sein)
    "led_panel": "light.{device_id}_led_panel",  # ESPHome Light
    "grow_light_switch": "switch.{device_id}_grow_light",  # ESPHome Switch
    
    # Outdoor climate sensors (für erweiterte Klimaregelung)
    "temperature_outside": "sensor.{device_id}_temperature_outside",
    "humidity_outside": "sensor.{device_id}_humidity_outside",
    "pressure_outside": "sensor.{device_id}_pressure_outside",
    "co2_outside": "sensor.{device_id}_co2_outside",
}

# Configuration Keys für externe Entitäten
CONF_EXTERNAL_LIGHT_ENTITY = "external_light_entity"
CONF_LIGHT_SCHEDULE_START = "light_schedule_start"
CONF_LIGHT_SCHEDULE_END = "light_schedule_end"

# Day/Night Configuration (ohne Lichtsensor)
DAY_NIGHT_CONFIG = {
    "temp_difference": 3.0,    # °C - Nachtabsenkung
    "vpd_difference": 0.2,     # kPa - VPD Reduktion nachts
    "humidity_increase": 5.0,  # % - Erhöhung der Luftfeuchtigkeit nachts
    "co2_reduction": 200,      # ppm - CO₂ Reduktion nachts
}

# Athena® Growth Phases with Day/Night Parameters
GROWTH_PHASES = {
    "vegetative": {
        "name": "Vegetative",
        "vwc_target": 75.0,
        "ec_target": 4.0,
        "ph_target": 6.0,
        # Tag-Parameter
        "vpd_target_day": 0.9,
        "temp_target_day": 25.0,
        "humidity_target_day": 65.0,
        "co2_target_day": 1200,
        # Nacht-Parameter
        "vpd_target_night": 0.7,
        "temp_target_night": 22.0,
        "humidity_target_night": 70.0,
        "co2_target_night": 1000,
        "dryback_target": 35.0,
    },
    "flowering_stretch": {
        "name": "Flowering Stretch",
        "vwc_target": 80.0,
        "ec_target": 5.0,
        "ph_target": 6.0,
        # Tag-Parameter
        "vpd_target_day": 1.0,
        "temp_target_day": 24.0,
        "humidity_target_day": 60.0,
        "co2_target_day": 1400,
        # Nacht-Parameter
        "vpd_target_night": 0.8,
        "temp_target_night": 21.0,
        "humidity_target_night": 65.0,
        "co2_target_night": 1200,
        "dryback_target": 40.0,
    },
    "flowering_bulk": {
        "name": "Flowering Bulk",
        "vwc_target": 85.0,
        "ec_target": 7.0,
        "ph_target": 6.0,
        # Tag-Parameter
        "vpd_target_day": 1.2,
        "temp_target_day": 22.0,
        "humidity_target_day": 55.0,
        "co2_target_day": 1500,
        # Nacht-Parameter
        "vpd_target_night": 1.0,
        "temp_target_night": 19.0,
        "humidity_target_night": 60.0,
        "co2_target_night": 1300,
        "dryback_target": 45.0,
    },
    "flowering_finish": {
        "name": "Flowering Finish",
        "vwc_target": 70.0,
        "ec_target": 3.0,
        "ph_target": 6.0,
        # Tag-Parameter
        "vpd_target_day": 1.4,
        "temp_target_day": 20.0,
        "humidity_target_day": 50.0,
        "co2_target_day": 1200,
        # Nacht-Parameter
        "vpd_target_night": 1.2,
        "temp_target_night": 17.0,
        "humidity_target_night": 55.0,
        "co2_target_night": 1000,
        "dryback_target": 50.0,
    },
}

# Crop Steering Strategies
CROP_STEERING_STRATEGIES = {
    "vegetative": {
        "name": "Vegetative Steering",
        "description": "Mehr Bewässerung, weniger Stress, fördert Wachstum",
        "shot_multiplier": 1.5,
        "dryback_reduction": 5.0,
        "ec_target_reduction": 1.0,
    },
    "generative": {
        "name": "Generative Steering", 
        "description": "Weniger Bewässerung, mehr Stress, fördert Blüte",
        "shot_multiplier": 0.8,
        "dryback_increase": 5.0,
        "ec_target_increase": 1.5,
    },
    "balanced": {
        "name": "Balanced Steering",
        "description": "Ausgewogene Strategie zwischen vegetativ und generativ",
        "shot_multiplier": 1.0,
        "dryback_adjustment": 0.0,
        "ec_target_adjustment": 0.0,
    },
}

# Irrigation Phases (P0-P3)
IRRIGATION_PHASES = {
    "P0": {
        "name": "Additional Dryback",
        "description": "Transpiration vor Bewässerung aktivieren",
        "duration_hours": 1.5,
        "additional_dryback": 3.0,
    },
    "P1": {
        "name": "Saturation",
        "description": "Substrate langsam sättigen",
        "shot_size_percent": 4.0,
        "interval_minutes": 20,
        "max_shots": 4,
    },
    "P2": {
        "name": "Maintenance", 
        "description": "Peak VWC Target halten",
        "trigger_dryback": 5.0,
        "shot_size_percent": 2.5,
    },
    "P3": {
        "name": "Overnight Dryback",
        "description": "Nächtliche Rücktrocknung",
        "target_dryback_veg": 35.0,
        "target_dryback_gen": 45.0,
    },
}

# Sensor Units
SENSOR_UNITS = {
    "temperature": "°C",
    "humidity": "%",
    "pressure": "hPa", 
    "vwc": "%",
    "ec_substrate": "ppm",
    "ph_substrate": "",
    "temp_substrate": "°C",
    "co2": "ppm",
    "light": "lx",
    "water_level": "%",
    "vpd_calculated": "kPa",
    "dryback_percent": "%",
}

# Alert Thresholds
ALERT_THRESHOLDS = {
    "vwc_critical_low": 50.0,
    "vwc_critical_high": 95.0,
    "ec_critical_low": 2.0,
    "ec_critical_high": 10.0,
    "ph_critical_low": 5.0,
    "ph_critical_high": 7.0,
    "temp_critical_low": 15.0,
    "temp_critical_high": 35.0,
    "vpd_critical_low": 0.5,
    "vpd_critical_high": 2.0,
}

# Device Classes
DEVICE_CLASSES = {
    "temperature": "temperature",
    "humidity": "humidity",
    "pressure": "pressure",
    "co2": "carbon_dioxide",
    "light": "illuminance",
    "water_level": None,
    "leak_sensor": "moisture",
}

# Climate Control Strategies
CLIMATE_STRATEGIES = {
    "maintain_optimal": {
        "name": "Optimale Bedingungen halten",
        "description": "Alle Parameter im Zielbereich",
        "actions": ["monitor", "fine_tune"]
    },
    "intake_air": {
        "name": "Außenluft nutzen",
        "description": "Günstige Außenbedingungen nutzen",
        "actions": ["increase_intake", "reduce_dehumidifier"]
    },
    "heat_dehumidify": {
        "name": "Heizen & Entfeuchten",
        "description": "VPD durch Temperaturerhöhung verbessern",
        "actions": ["increase_heating", "increase_dehumidifier"]
    },
    "cool_humidify": {
        "name": "Kühlen & Befeuchten", 
        "description": "VPD durch Kühlung und Befeuchtung verbessern",
        "actions": ["increase_exhaust", "increase_humidifier"]
    },
    "dehumidify_only": {
        "name": "Nur Entfeuchten",
        "description": "Luftfeuchtigkeit ohne Temperaturänderung senken",
        "actions": ["increase_dehumidifier", "increase_circulation"]
    },
    "humidify_only": {
        "name": "Nur Befeuchten",
        "description": "Luftfeuchtigkeit ohne Temperaturänderung erhöhen", 
        "actions": ["increase_humidifier", "reduce_exhaust"]
    },
    "cooling_ventilation": {
        "name": "Kühlende Belüftung",
        "description": "Außenluft zur Kühlung nutzen",
        "actions": ["maximum_intake", "increase_exhaust"]
    },
    "cooling_only": {
        "name": "Aktive Kühlung",
        "description": "Kühlung ohne Außenluft",
        "actions": ["increase_exhaust", "reduce_heating"]
    },
    "heating": {
        "name": "Heizen",
        "description": "Temperatur erhöhen",
        "actions": ["increase_heating", "reduce_intake"]
    }
}

# Ventilation Recommendations
VENTILATION_MODES = {
    "reduce_intake": {
        "intake_fan": 20,    # Prozent
        "exhaust_fan": 60,
        "circulation_fan": 80,
        "description": "Reduzierte Zuluft"
    },
    "normal": {
        "intake_fan": 60,
        "exhaust_fan": 60, 
        "circulation_fan": 80,
        "description": "Normale Belüftung"
    },
    "increase_intake": {
        "intake_fan": 80,
        "exhaust_fan": 60,
        "circulation_fan": 100,
        "description": "Erhöhte Zuluft"
    },
    "increase_exhaust": {
        "intake_fan": 60,
        "exhaust_fan": 80,
        "circulation_fan": 80,
        "description": "Erhöhte Abluft"
    },
    "maximum_intake": {
        "intake_fan": 100,
        "exhaust_fan": 80,
        "circulation_fan": 100,
        "description": "Maximale Zuluft"
    },
    "reduce_exhaust": {
        "intake_fan": 40,
        "exhaust_fan": 40,
        "circulation_fan": 100,
        "description": "Reduzierte Abluft"
    }
}
