"""Binary sensor platform for Athena Plant Monitor."""
import logging
from typing import Any, Dict, Optional

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DATA_COORDINATOR
from .coordinator import AthenaPlantCoordinator

_LOGGER = logging.getLogger(__name__)

BINARY_SENSOR_DESCRIPTIONS = [
    BinarySensorEntityDescription(
        key="leak_sensor",
        name="Leckage Sensor",
        device_class=BinarySensorDeviceClass.MOISTURE,
        icon="mdi:water-alert",
    ),
    BinarySensorEntityDescription(
        key="lights_on",
        name="Licht Status",
        icon="mdi:lightbulb",
    ),
    BinarySensorEntityDescription(
        key="pump_active",
        name="Pumpe Aktiv",
        icon="mdi:water-pump",
    ),
    BinarySensorEntityDescription(
        key="automation_enabled",
        name="Automatisierung Aktiv",
        icon="mdi:auto-mode",
    ),
    BinarySensorEntityDescription(
        key="vwc_in_range",
        name="VWC im Zielbereich",
        icon="mdi:check-circle",
    ),
    BinarySensorEntityDescription(
        key="ec_in_range",
        name="EC im Zielbereich",
        icon="mdi:check-circle",
    ),
    BinarySensorEntityDescription(
        key="ph_in_range",
        name="pH im Zielbereich",
        icon="mdi:check-circle",
    ),
    BinarySensorEntityDescription(
        key="vpd_in_range",
        name="VPD im Zielbereich",
        icon="mdi:check-circle",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_COORDINATOR]

    entities = []
    for description in BINARY_SENSOR_DESCRIPTIONS:
        entities.append(AthenaPlantBinarySensor(coordinator, description))

    async_add_entities(entities)


class AthenaPlantBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of an Athena Plant Monitor binary sensor."""

    def __init__(
        self,
        coordinator: AthenaPlantCoordinator,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device_id}_binary_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> Optional[bool]:
        """Return true if the binary sensor is on."""
        key = self.entity_description.key
        
        if key == "leak_sensor":
            # Get ESPHome leak sensor state
            return self.coordinator.data.get("leak_sensor") == "on"
        
        elif key == "lights_on":
            return self.coordinator.data.get("irrigation_state", {}).get("lights_on", False)
        
        elif key == "pump_active":
            return self.coordinator.data.get("pump") == "on"
        
        elif key == "automation_enabled":
            return self.coordinator.data.get("irrigation_state", {}).get("automation_enabled", True)
        
        elif key == "vwc_in_range":
            vwc = self.coordinator.data.get("vwc")
            target = self.coordinator.data.get("vwc_target")
            if vwc is not None and target is not None:
                return abs(vwc - target) <= target * 0.1  # Within 10%
        
        elif key == "ec_in_range":
            ec = self.coordinator.data.get("ec_substrate")
            target = self.coordinator.data.get("ec_target")
            if ec is not None and target is not None:
                return abs(ec - target) <= target * 0.15  # Within 15%
        
        elif key == "ph_in_range":
            ph = self.coordinator.data.get("ph_substrate")
            target = self.coordinator.data.get("ph_target")
            if ph is not None and target is not None:
                return abs(ph - target) <= 0.3  # Within 0.3 pH units
        
        elif key == "vpd_in_range":
            vpd = self.coordinator.data.get("vpd_calculated")
            target = self.coordinator.data.get("vpd_target")
            if vpd is not None and target is not None:
                return abs(vpd - target) <= 0.2  # Within 0.2 kPa
        
        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        key = self.entity_description.key
        
        # Add range check details
        if key.endswith("_in_range"):
            sensor_key = key.replace("_in_range", "").replace("_substrate", "").replace("_calculated", "")
            current = self.coordinator.data.get(sensor_key) or self.coordinator.data.get(f"{sensor_key}_substrate") or self.coordinator.data.get(f"{sensor_key}_calculated")
            target = self.coordinator.data.get(f"{sensor_key}_target")
            
            if current is not None and target is not None:
                attrs.update({
                    "current_value": current,
                    "target_value": target,
                    "deviation": round(current - target, 2),
                    "deviation_percent": round(((current - target) / target) * 100, 1) if target != 0 else 0,
                })
        
        # Add irrigation state context
        irrigation_state = self.coordinator.data.get("irrigation_state", {})
        growth_config = self.coordinator.data.get("growth_config", {})
        
        attrs.update({
            "growth_phase": growth_config.get("phase"),
            "crop_steering": growth_config.get("steering"),
            "current_irrigation_phase": irrigation_state.get("current_phase"),
        })
        
        return attrs
