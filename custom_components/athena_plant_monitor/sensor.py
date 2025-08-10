"""Sensor platform for Athena Plant Monitor."""
import logging
from typing import Any, Dict, Optional

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfPressure,
    CONCENTRATION_PARTS_PER_MILLION,
    UnitOfIlluminance,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    DATA_COORDINATOR,
    SENSOR_UNITS,
    DEVICE_CLASSES,
)
from .coordinator import AthenaPlantCoordinator

_LOGGER = logging.getLogger(__name__)

# Sensor descriptions
SENSOR_DESCRIPTIONS = [
    # Environmental sensors
    SensorEntityDescription(
        key="temperature",
        name="Lufttemperatur",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
    ),
    SensorEntityDescription(
        key="humidity",
        name="Luftfeuchtigkeit",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:water-percent",
    ),
    SensorEntityDescription(
        key="pressure",
        name="Luftdruck",
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPressure.HPA,
        icon="mdi:gauge",
    ),
    SensorEntityDescription(
        key="co2",
        name="CO₂ Konzentration",
        device_class=SensorDeviceClass.CARBON_DIOXIDE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        icon="mdi:molecule-co2",
    ),
    SensorEntityDescription(
        key="light",
        name="Lichtintensität",
        device_class=SensorDeviceClass.ILLUMINANCE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfIlluminance.LUX,
        icon="mdi:brightness-6",
    ),
    
    # Substrate sensors
    SensorEntityDescription(
        key="vwc",
        name="VWC Substratfeuchte",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:water-circle",
    ),
    SensorEntityDescription(
        key="ec_substrate",
        name="EC Substrat",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        icon="mdi:lightning-bolt-circle",
    ),
    SensorEntityDescription(
        key="ph_substrate",
        name="pH Substrat",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:ph",
    ),
    SensorEntityDescription(
        key="temp_substrate",
        name="Substrattemperatur",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-low",
    ),
    SensorEntityDescription(
        key="water_level",
        name="Wassertank Füllstand",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:water-well",
    ),
    
    # Calculated sensors
    SensorEntityDescription(
        key="vpd_calculated",
        name="VPD (berechnet)",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="kPa",
        icon="mdi:air-filter",
    ),
    SensorEntityDescription(
        key="vpd_outside",
        name="VPD Außen (berechnet)",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="kPa",
        icon="mdi:weather-partly-cloudy",
    ),
    SensorEntityDescription(
        key="dryback_percent",
        name="Dryback Prozent",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:trending-down",
    ),
    
    # Target sensors
    SensorEntityDescription(
        key="vwc_target",
        name="VWC Zielwert",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:bullseye-arrow",
    ),
    SensorEntityDescription(
        key="ec_target",
        name="EC Zielwert",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        icon="mdi:bullseye-arrow",
    ),
    SensorEntityDescription(
        key="ph_target",
        name="pH Zielwert",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:bullseye-arrow",
    ),
    SensorEntityDescription(
        key="vpd_target",
        name="VPD Zielwert",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="kPa",
        icon="mdi:bullseye-arrow",
    ),
    SensorEntityDescription(
        key="temp_target",
        name="Temperatur Zielwert",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:bullseye-arrow",
    ),
    SensorEntityDescription(
        key="humidity_target",
        name="Luftfeuchtigkeit Zielwert",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:bullseye-arrow",
    ),
    SensorEntityDescription(
        key="dryback_target",
        name="Dryback Zielwert",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:bullseye-arrow",
    ),
]

# Status sensors
STATUS_SENSOR_DESCRIPTIONS = [
    SensorEntityDescription(
        key="current_phase",
        name="Aktuelle Irrigationsphase",
        icon="mdi:timeline-clock",
    ),
    SensorEntityDescription(
        key="growth_phase",
        name="Wachstumsphase",
        icon="mdi:sprout",
    ),
    SensorEntityDescription(
        key="crop_steering",
        name="Crop Steering Strategie",
        icon="mdi:strategy",
    ),
    SensorEntityDescription(
        key="daily_water_total",
        name="Tageswassermenge",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="L",
        icon="mdi:water-pump",
    ),
    SensorEntityDescription(
        key="max_vwc_today",
        name="Max VWC Heute",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:trending-up",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_COORDINATOR]

    entities = []
    
    # Add main sensors
    for description in SENSOR_DESCRIPTIONS:
        entities.append(AthenaPlantSensor(coordinator, description))
    
    # Add status sensors
    for description in STATUS_SENSOR_DESCRIPTIONS:
        entities.append(AthenaPlantStatusSensor(coordinator, description))

    # Add alert sensors
    entities.extend([
        AthenaPlantAlertSensor(coordinator, "critical", "Kritische Alerts"),
        AthenaPlantAlertSensor(coordinator, "warning", "Warnungen"),
        AthenaPlantAlertSensor(coordinator, "info", "Informationen"),
    ])

    async_add_entities(entities)


class AthenaPlantSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Athena Plant Monitor sensor."""

    def __init__(
        self,
        coordinator: AthenaPlantCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device_id}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> Optional[float]:
        """Return the native value of the sensor."""
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        
        key = self.entity_description.key
        
        # Add target comparison for main sensors
        if key in ["vwc", "ec_substrate", "ph_substrate", "vpd_calculated", "temperature", "humidity"]:
            target_key = f"{key.replace('_substrate', '').replace('_calculated', '')}_target"
            target_value = self.coordinator.data.get(target_key)
            current_value = self.coordinator.data.get(key)
            
            if target_value is not None and current_value is not None:
                attrs["target"] = target_value
                attrs["deviation"] = round(current_value - target_value, 2)
                attrs["deviation_percent"] = round(((current_value - target_value) / target_value) * 100, 1) if target_value != 0 else 0
        
        # Add growth phase context
        growth_config = self.coordinator.data.get("growth_config", {})
        attrs.update({
            "growth_phase": growth_config.get("phase"),
            "crop_steering": growth_config.get("steering"),
        })
        
        return attrs


class AthenaPlantStatusSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Athena Plant Monitor status sensor."""

    def __init__(
        self,
        coordinator: AthenaPlantCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the status sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device_id}_status_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> Optional[str]:
        """Return the native value of the sensor."""
        key = self.entity_description.key
        
        if key == "current_phase":
            return self.coordinator.data.get("irrigation_state", {}).get("current_phase")
        elif key == "growth_phase":
            return self.coordinator.data.get("growth_config", {}).get("phase")
        elif key == "crop_steering":
            return self.coordinator.data.get("growth_config", {}).get("steering")
        elif key == "daily_water_total":
            return self.coordinator.data.get("irrigation_state", {}).get("daily_water_total", 0)
        elif key == "max_vwc_today":
            return self.coordinator.data.get("irrigation_state", {}).get("max_vwc_today", 0)
        
        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        
        irrigation_state = self.coordinator.data.get("irrigation_state", {})
        growth_config = self.coordinator.data.get("growth_config", {})
        
        if self.entity_description.key == "current_phase":
            attrs.update({
                "lights_on": irrigation_state.get("lights_on"),
                "automation_enabled": irrigation_state.get("automation_enabled"),
                "last_irrigation": irrigation_state.get("last_irrigation"),
            })
        
        attrs.update({
            "growth_phase": growth_config.get("phase"),
            "crop_steering": growth_config.get("steering"),
            "substrate_size": growth_config.get("substrate_size"),
        })
        
        return attrs


class AthenaPlantAlertSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Athena Plant Monitor alert sensor."""

    def __init__(
        self,
        coordinator: AthenaPlantCoordinator,
        alert_type: str,
        name: str,
    ) -> None:
        """Initialize the alert sensor."""
        super().__init__(coordinator)
        self.alert_type = alert_type
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.device_id}_alerts_{alert_type}"
        self._attr_device_info = coordinator.device_info
        self._attr_icon = {
            "critical": "mdi:alert-circle",
            "warning": "mdi:alert",
            "info": "mdi:information",
        }.get(alert_type, "mdi:alert")

    @property
    def native_value(self) -> int:
        """Return the number of alerts."""
        alerts = self.coordinator.data.get("alerts", {})
        return len(alerts.get(self.alert_type, []))

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return alert details."""
        alerts = self.coordinator.data.get("alerts", {})
        alert_list = alerts.get(self.alert_type, [])
        
        attrs = {
            "alerts": alert_list,
            "count": len(alert_list),
        }
        
        if alert_list:
            attrs["latest_alert"] = alert_list[-1]
            attrs["messages"] = [alert["message"] for alert in alert_list]
        
        return attrs
