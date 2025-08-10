"""Switch platform for Athena Plant Monitor."""
import logging
from typing import Any, Dict, Optional

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DATA_COORDINATOR
from .coordinator import AthenaPlantCoordinator

_LOGGER = logging.getLogger(__name__)

SWITCH_DESCRIPTIONS = [
    SwitchEntityDescription(
        key="automation_enabled",
        name="Automatische Bewässerung",
        icon="mdi:auto-mode",
    ),
    SwitchEntityDescription(
        key="manual_pump",
        name="Manuelle Pumpe",
        icon="mdi:water-pump",
    ),
    SwitchEntityDescription(
        key="fan_intake",
        name="Zuluftventilator",
        icon="mdi:fan",
    ),
    SwitchEntityDescription(
        key="fan_exhaust",
        name="Abluftventilator",
        icon="mdi:fan",
    ),
    SwitchEntityDescription(
        key="humidifier",
        name="Luftbefeuchter",
        icon="mdi:air-humidifier",
    ),
    SwitchEntityDescription(
        key="dehumidifier",
        name="Luftentfeuchter",
        icon="mdi:air-humidifier-off",
    ),
    SwitchEntityDescription(
        key="co2_valve",
        name="CO₂ Ventil",
        icon="mdi:valve",
    ),
    SwitchEntityDescription(
        key="auto_climate_control",
        name="Automatische Klimaregelung",
        icon="mdi:thermostat-auto",
    ),
    SwitchEntityDescription(
        key="vpd_optimization",
        name="VPD Optimierung",
        icon="mdi:auto-fix",
    ),
    SwitchEntityDescription(
        key="emergency_ventilation",
        name="Notfall-Lüftung",
        icon="mdi:fan-alert",
    ),
    SwitchEntityDescription(
        key="external_grow_light",
        name="Wachstumslicht (extern)",
        icon="mdi:lightbulb-on",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_COORDINATOR]

    entities = []
    for description in SWITCH_DESCRIPTIONS:
        entities.append(AthenaPlantSwitch(coordinator, description))

    async_add_entities(entities)


class AthenaPlantSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of an Athena Plant Monitor switch."""

    def __init__(
        self,
        coordinator: AthenaPlantCoordinator,
        description: SwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device_id}_switch_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def is_on(self) -> Optional[bool]:
        """Return true if switch is on."""
        key = self.entity_description.key
        
        if key == "automation_enabled":
            return self.coordinator.data.get("irrigation_state", {}).get("automation_enabled", True)
        elif key == "manual_pump":
            return self.coordinator.data.get("pump") == "on"
        elif key == "auto_climate_control":
            return self.coordinator.data.get("climate_control", {}).get("auto_enabled", False)
        elif key == "vpd_optimization":
            return self.coordinator.data.get("climate_control", {}).get("vpd_optimization", False)
        elif key == "emergency_ventilation":
            return self.coordinator.data.get("climate_control", {}).get("emergency_mode", False)
        elif key == "external_grow_light":
            # Prüfe externe Lichtentität
            external_light_entity = self.coordinator._external_light_entity
            if external_light_entity:
                external_state = self.hass.states.get(external_light_entity)
                return external_state and external_state.state == "on"
            return False
        else:
            # For ESPHome entities, get state
            return self.coordinator.data.get(key) == "on"

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        key = self.entity_description.key
        
        if key == "automation_enabled":
            # Update internal state
            self.coordinator._irrigation_state["automation_enabled"] = True
            await self.coordinator.async_request_refresh()
            
        elif key == "manual_pump":
            # Turn on ESPHome pump
            pump_entity = self.coordinator.get_entity_id("pump")
            if pump_entity:
                await self.hass.services.async_call(
                    "switch", "turn_on",
                    {"entity_id": pump_entity}
                )
        elif key == "auto_climate_control":
            # Enable automatic climate control
            if not hasattr(self.coordinator, '_climate_control'):
                self.coordinator._climate_control = {}
            self.coordinator._climate_control["auto_enabled"] = True
            await self.coordinator.apply_climate_strategy()  # Apply optimal strategy
            await self.coordinator.async_request_refresh()
            
        elif key == "vpd_optimization":
            # Enable VPD optimization
            if not hasattr(self.coordinator, '_climate_control'):
                self.coordinator._climate_control = {}
            self.coordinator._climate_control["vpd_optimization"] = True
            await self.coordinator.optimize_vpd()  # Start VPD optimization
            await self.coordinator.async_request_refresh()
            
        elif key == "emergency_ventilation":
            # Emergency ventilation mode
            if not hasattr(self.coordinator, '_climate_control'):
                self.coordinator._climate_control = {}
            self.coordinator._climate_control["emergency_mode"] = True
            await self.coordinator.set_ventilation_mode("maximum_intake")
            await self.coordinator.async_request_refresh()
        elif key == "external_grow_light":
            # Steuerung der externen Lichtentität
            external_light_entity = self.coordinator._external_light_entity
            if external_light_entity:
                await self.hass.services.async_call(
                    external_light_entity.split(".")[0], "turn_on",
                    {"entity_id": external_light_entity}
                )
                await self.coordinator.async_request_refresh()
        else:
            # Control ESPHome entity
            entity_id = self.coordinator.get_entity_id(key)
            if entity_id:
                await self.hass.services.async_call(
                    "switch", "turn_on",
                    {"entity_id": entity_id}
                )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        key = self.entity_description.key
        
        if key == "automation_enabled":
            # Update internal state
            self.coordinator._irrigation_state["automation_enabled"] = False
            await self.coordinator.async_request_refresh()
            
        elif key == "manual_pump":
            # Turn off ESPHome pump
            pump_entity = self.coordinator.get_entity_id("pump")
            if pump_entity:
                await self.hass.services.async_call(
                    "switch", "turn_off",
                    {"entity_id": pump_entity}
                )
        elif key == "auto_climate_control":
            # Disable automatic climate control
            if hasattr(self.coordinator, '_climate_control'):
                self.coordinator._climate_control["auto_enabled"] = False
            await self.coordinator.async_request_refresh()
            
        elif key == "vpd_optimization":
            # Disable VPD optimization
            if hasattr(self.coordinator, '_climate_control'):
                self.coordinator._climate_control["vpd_optimization"] = False
            await self.coordinator.async_request_refresh()
            
        elif key == "emergency_ventilation":
            # Disable emergency ventilation
            if hasattr(self.coordinator, '_climate_control'):
                self.coordinator._climate_control["emergency_mode"] = False
            await self.coordinator.set_ventilation_mode("normal")  # Return to normal
            await self.coordinator.async_request_refresh()
        elif key == "external_grow_light":
            # Ausschalten der externen Lichtentität
            external_light_entity = self.coordinator._external_light_entity
            if external_light_entity:
                await self.hass.services.async_call(
                    external_light_entity.split(".")[0], "turn_off",
                    {"entity_id": external_light_entity}
                )
                await self.coordinator.async_request_refresh()
            await self.coordinator.async_request_refresh()
        else:
            # Control ESPHome entity
            entity_id = self.coordinator.get_entity_id(key)
            if entity_id:
                await self.hass.services.async_call(
                    "switch", "turn_off",
                    {"entity_id": entity_id}
                )

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        
        # Add context information
        irrigation_state = self.coordinator.data.get("irrigation_state", {})
        growth_config = self.coordinator.data.get("growth_config", {})
        
        attrs.update({
            "growth_phase": growth_config.get("phase"),
            "crop_steering": growth_config.get("steering"),
            "current_irrigation_phase": irrigation_state.get("current_phase"),
        })
        
        # Add specific attributes for pump
        if self.entity_description.key == "manual_pump":
            attrs.update({
                "last_irrigation": irrigation_state.get("last_irrigation"),
                "daily_water_total": irrigation_state.get("daily_water_total", 0),
                "automation_enabled": irrigation_state.get("automation_enabled", True),
            })
        
        return attrs
