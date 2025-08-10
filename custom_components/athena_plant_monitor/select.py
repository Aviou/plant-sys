"""Select platform for Athena Plant Monitor."""
import logging
from typing import Any, Dict, Optional

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    DATA_COORDINATOR,
    GROWTH_PHASES,
    CROP_STEERING_STRATEGIES,
)
from .coordinator import AthenaPlantCoordinator

_LOGGER = logging.getLogger(__name__)

SELECT_DESCRIPTIONS = [
    SelectEntityDescription(
        key="growth_phase",
        name="Wachstumsphase",
        icon="mdi:sprout",
        options=list(GROWTH_PHASES.keys()),
    ),
    SelectEntityDescription(
        key="crop_steering",
        name="Crop Steering Strategie",
        icon="mdi:strategy",
        options=list(CROP_STEERING_STRATEGIES.keys()),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_COORDINATOR]

    entities = []
    for description in SELECT_DESCRIPTIONS:
        entities.append(AthenaPlantSelect(coordinator, description))

    async_add_entities(entities)


class AthenaPlantSelect(CoordinatorEntity, SelectEntity):
    """Representation of an Athena Plant Monitor select entity."""

    def __init__(
        self,
        coordinator: AthenaPlantCoordinator,
        description: SelectEntityDescription,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device_id}_select_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def current_option(self) -> Optional[str]:
        """Return the current selected option."""
        key = self.entity_description.key
        
        if key == "growth_phase":
            return self.coordinator._growth_config.get("phase", "vegetative")
        elif key == "crop_steering":
            return self.coordinator._growth_config.get("steering", "vegetative")
        
        return None

    async def async_select_option(self, option: str) -> None:
        """Select an option."""
        key = self.entity_description.key
        
        if key == "growth_phase" and option in GROWTH_PHASES:
            await self.coordinator.set_growth_phase(option)
        elif key == "crop_steering" and option in CROP_STEERING_STRATEGIES:
            await self.coordinator.set_crop_steering(option)

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        key = self.entity_description.key
        current_option = self.current_option
        
        if key == "growth_phase" and current_option:
            phase_config = GROWTH_PHASES.get(current_option, {})
            attrs.update({
                "phase_name": phase_config.get("name"),
                "recommended_vwc": phase_config.get("vwc_target"),
                "recommended_ec": phase_config.get("ec_target"),
                "recommended_ph": phase_config.get("ph_target"),
                "recommended_vpd": phase_config.get("vpd_target"),
                "recommended_temp": phase_config.get("temp_target"),
                "recommended_humidity": phase_config.get("humidity_target"),
                "recommended_dryback": phase_config.get("dryback_target"),
            })
        
        elif key == "crop_steering" and current_option:
            strategy_config = CROP_STEERING_STRATEGIES.get(current_option, {})
            attrs.update({
                "strategy_name": strategy_config.get("name"),
                "description": strategy_config.get("description"),
                "shot_multiplier": strategy_config.get("shot_multiplier"),
            })
            
            # Add specific adjustments
            if "dryback_reduction" in strategy_config:
                attrs["dryback_adjustment"] = f"-{strategy_config['dryback_reduction']}%"
            elif "dryback_increase" in strategy_config:
                attrs["dryback_adjustment"] = f"+{strategy_config['dryback_increase']}%"
            else:
                attrs["dryback_adjustment"] = "0%"
                
            if "ec_target_reduction" in strategy_config:
                attrs["ec_adjustment"] = f"-{strategy_config['ec_target_reduction']} ppm"
            elif "ec_target_increase" in strategy_config:
                attrs["ec_adjustment"] = f"+{strategy_config['ec_target_increase']} ppm"
            else:
                attrs["ec_adjustment"] = "0 ppm"
        
        # Add current irrigation state
        irrigation_state = self.coordinator.data.get("irrigation_state", {})
        attrs.update({
            "current_irrigation_phase": irrigation_state.get("current_phase"),
            "lights_on": irrigation_state.get("lights_on"),
            "automation_enabled": irrigation_state.get("automation_enabled"),
        })
        
        return attrs
