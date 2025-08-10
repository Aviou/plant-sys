"""Button platform for Athena Plant Monitor."""
import logging
from typing import Any, Dict

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DATA_COORDINATOR
from .coordinator import AthenaPlantCoordinator

_LOGGER = logging.getLogger(__name__)

BUTTON_DESCRIPTIONS = [
    ButtonEntityDescription(
        key="irrigation_shot_small",
        name="Kleiner Bewässerungsschuss (2%)",
        icon="mdi:water",
    ),
    ButtonEntityDescription(
        key="irrigation_shot_medium",
        name="Mittlerer Bewässerungsschuss (3%)",
        icon="mdi:water",
    ),
    ButtonEntityDescription(
        key="irrigation_shot_large",
        name="Großer Bewässerungsschuss (5%)",
        icon="mdi:water",
    ),
    ButtonEntityDescription(
        key="irrigation_shot_custom",
        name="Benutzerdefinierter Bewässerungsschuss",
        icon="mdi:water-plus",
    ),
    ButtonEntityDescription(
        key="reset_daily_water",
        name="Tageswasserzähler zurücksetzen",
        icon="mdi:counter",
    ),
    ButtonEntityDescription(
        key="reset_max_vwc",
        name="Max VWC zurücksetzen",
        icon="mdi:restart",
    ),
    ButtonEntityDescription(
        key="calibrate_sensors",
        name="Sensoren kalibrieren",
        icon="mdi:tune",
    ),
    ButtonEntityDescription(
        key="emergency_stop",
        name="Notfall-Stopp",
        icon="mdi:emergency",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_COORDINATOR]

    entities = []
    for description in BUTTON_DESCRIPTIONS:
        entities.append(AthenaPlantButton(coordinator, description))

    async_add_entities(entities)


class AthenaPlantButton(CoordinatorEntity, ButtonEntity):
    """Representation of an Athena Plant Monitor button."""

    def __init__(
        self,
        coordinator: AthenaPlantCoordinator,
        description: ButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device_id}_button_{description.key}"
        self._attr_device_info = coordinator.device_info

    async def async_press(self) -> None:
        """Handle button press."""
        key = self.entity_description.key
        
        try:
            if key == "irrigation_shot_small":
                await self.coordinator.trigger_irrigation_shot(2.0, 20)
                
            elif key == "irrigation_shot_medium":
                await self.coordinator.trigger_irrigation_shot(3.0, 30)
                
            elif key == "irrigation_shot_large":
                await self.coordinator.trigger_irrigation_shot(5.0, 50)
                
            elif key == "irrigation_shot_custom":
                # Get custom values from number entities
                shot_size = 3.0  # Default, would be read from number entity
                duration = 30    # Default, would be read from number entity
                await self.coordinator.trigger_irrigation_shot(shot_size, duration)
                
            elif key == "reset_daily_water":
                self.coordinator._irrigation_state["daily_water_total"] = 0.0
                await self.coordinator.async_request_refresh()
                
            elif key == "reset_max_vwc":
                self.coordinator._irrigation_state["max_vwc_today"] = 0.0
                await self.coordinator.async_request_refresh()
                
            elif key == "calibrate_sensors":
                # Trigger sensor calibration (would call ESPHome calibration services)
                _LOGGER.info("Sensor calibration triggered")
                # Here you would call specific ESPHome calibration services
                
            elif key == "emergency_stop":
                # Emergency stop: turn off all pumps and automation
                self.coordinator._irrigation_state["automation_enabled"] = False
                
                # Turn off pump
                pump_entity = self.coordinator.get_entity_id("pump")
                if pump_entity:
                    await self.hass.services.async_call(
                        "switch", "turn_off",
                        {"entity_id": pump_entity}
                    )
                
                _LOGGER.warning("Emergency stop activated - all irrigation stopped")
                await self.coordinator.async_request_refresh()
                
        except Exception as err:
            _LOGGER.error(f"Error executing button action {key}: {err}")

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        key = self.entity_description.key
        
        # Add context for irrigation buttons
        if key.startswith("irrigation_shot"):
            irrigation_state = self.coordinator.data.get("irrigation_state", {})
            growth_config = self.coordinator.data.get("growth_config", {})
            
            attrs.update({
                "substrate_size": growth_config.get("substrate_size", 10.0),
                "daily_water_total": irrigation_state.get("daily_water_total", 0),
                "automation_enabled": irrigation_state.get("automation_enabled", True),
                "current_phase": irrigation_state.get("current_phase"),
            })
            
            # Calculate water amount for specific shot sizes
            substrate_size = growth_config.get("substrate_size", 10.0)
            if key == "irrigation_shot_small":
                attrs["water_amount"] = f"{(2.0 / 100) * substrate_size:.1f}L"
            elif key == "irrigation_shot_medium":
                attrs["water_amount"] = f"{(3.0 / 100) * substrate_size:.1f}L"
            elif key == "irrigation_shot_large":
                attrs["water_amount"] = f"{(5.0 / 100) * substrate_size:.1f}L"
        
        # Add growth context
        growth_config = self.coordinator.data.get("growth_config", {})
        attrs.update({
            "growth_phase": growth_config.get("phase"),
            "crop_steering": growth_config.get("steering"),
        })
        
        return attrs
