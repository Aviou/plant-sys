"""Config flow for Athena Plant Monitor integration."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity_registry import async_get
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_DEVICE_ID,
    CONF_UPDATE_INTERVAL,
    CONF_GROWTH_PHASE,
    CONF_CROP_STEERING,
    CONF_SUBSTRATE_SIZE,
    CONF_VWC_TARGET,
    CONF_EC_TARGET,
    CONF_PH_TARGET,
    CONF_VPD_TARGET,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_SUBSTRATE_SIZE,
    DEFAULT_VWC_TARGET,
    DEFAULT_EC_TARGET,
    DEFAULT_PH_TARGET,
    DEFAULT_VPD_TARGET,
    GROWTH_PHASES,
    CROP_STEERING_STRATEGIES,
)

_LOGGER = logging.getLogger(__name__)


class AthenaPlantConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Athena Plant Monitor."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_devices: Dict[str, str] = {}
        self._device_id: Optional[str] = None

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate device exists
            device_id = user_input[CONF_DEVICE_ID]
            if await self._async_device_exists(device_id):
                await self.async_set_unique_id(device_id)
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=f"Athena Plant Monitor ({device_id})",
                    data=user_input,
                )
            else:
                errors[CONF_DEVICE_ID] = "device_not_found"

        # Discover ESPHome devices
        discovered_devices = await self._async_discover_esphome_devices()

        data_schema = vol.Schema({
            vol.Required(CONF_DEVICE_ID): vol.In(list(discovered_devices.keys())) if discovered_devices else str,
            vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): vol.Coerce(int),
            vol.Optional(CONF_GROWTH_PHASE, default="vegetative"): vol.In(list(GROWTH_PHASES.keys())),
            vol.Optional(CONF_CROP_STEERING, default="vegetative"): vol.In(list(CROP_STEERING_STRATEGIES.keys())),
            vol.Optional(CONF_SUBSTRATE_SIZE, default=DEFAULT_SUBSTRATE_SIZE): vol.Coerce(float),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "discovered_devices": "\n".join([f"• {name} ({device_id})" for device_id, name in discovered_devices.items()]),
            },
        )

    async def async_step_advanced(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle advanced configuration step."""
        if user_input is not None:
            # Merge with existing data
            data = {**self._device_data, **user_input}
            return self.async_create_entry(
                title=f"Athena Plant Monitor ({self._device_id})",
                data=data,
            )

        data_schema = vol.Schema({
            vol.Optional(CONF_VWC_TARGET, default=DEFAULT_VWC_TARGET): vol.Coerce(float),
            vol.Optional(CONF_EC_TARGET, default=DEFAULT_EC_TARGET): vol.Coerce(float),
            vol.Optional(CONF_PH_TARGET, default=DEFAULT_PH_TARGET): vol.Coerce(float),
            vol.Optional(CONF_VPD_TARGET, default=DEFAULT_VPD_TARGET): vol.Coerce(float),
        })

        return self.async_show_form(
            step_id="advanced",
            data_schema=data_schema,
        )

    async def _async_discover_esphome_devices(self) -> Dict[str, str]:
        """Discover ESPHome devices that could be plant monitors."""
        discovered = {}
        
        # Get device registry
        device_registry = dr.async_get(self.hass)
        entity_registry = async_get(self.hass)
        
        # Look for devices with typical ESPHome plant monitoring entities
        for device in device_registry.devices.values():
            if device.name and "esphome" in str(device.identifiers):
                # Check if device has typical plant monitoring entities
                device_entities = [
                    entity.entity_id for entity in entity_registry.entities.values()
                    if entity.device_id == device.id
                ]
                
                # Look for typical plant monitoring sensors
                has_vwc = any("vwc" in entity_id for entity_id in device_entities)
                has_pump = any("pump" in entity_id for entity_id in device_entities)
                has_temp = any("temperature" in entity_id for entity_id in device_entities)
                
                if has_vwc or has_pump or (has_temp and len(device_entities) > 3):
                    # Extract device ID from entity IDs
                    for entity_id in device_entities:
                        if entity_id.startswith("sensor."):
                            parts = entity_id.split("_")
                            if len(parts) >= 3:
                                device_id = "_".join(parts[1:-1])  # Extract middle part as device ID
                                discovered[device_id] = device.name or device_id
                                break
        
        return discovered

    async def _async_device_exists(self, device_id: str) -> bool:
        """Check if the ESPHome device exists and has required entities."""
        entity_registry = async_get(self.hass)
        
        # Check for required entities
        required_entities = [
            f"sensor.{device_id}_vwc",
            f"switch.{device_id}_pump",
        ]
        
        for entity_id in required_entities:
            if entity_id not in entity_registry.entities:
                _LOGGER.warning(f"Required entity {entity_id} not found")
                return False
        
        return True

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> "AthenaPlantOptionsFlow":
        """Get the options flow for this handler."""
        return AthenaPlantOptionsFlow(config_entry)


class AthenaPlantOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Athena Plant Monitor."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_config = self.config_entry.data
        
        data_schema = vol.Schema({
            vol.Optional(
                CONF_UPDATE_INTERVAL,
                default=current_config.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
            ): vol.Coerce(int),
            vol.Optional(
                CONF_GROWTH_PHASE,
                default=current_config.get(CONF_GROWTH_PHASE, "vegetative")
            ): vol.In(list(GROWTH_PHASES.keys())),
            vol.Optional(
                CONF_CROP_STEERING,
                default=current_config.get(CONF_CROP_STEERING, "vegetative")
            ): vol.In(list(CROP_STEERING_STRATEGIES.keys())),
            vol.Optional(
                CONF_SUBSTRATE_SIZE,
                default=current_config.get(CONF_SUBSTRATE_SIZE, DEFAULT_SUBSTRATE_SIZE)
            ): vol.Coerce(float),
            vol.Optional(
                CONF_VWC_TARGET,
                default=current_config.get(CONF_VWC_TARGET, DEFAULT_VWC_TARGET)
            ): vol.Coerce(float),
            vol.Optional(
                CONF_EC_TARGET,
                default=current_config.get(CONF_EC_TARGET, DEFAULT_EC_TARGET)
            ): vol.Coerce(float),
            vol.Optional(
                CONF_PH_TARGET,
                default=current_config.get(CONF_PH_TARGET, DEFAULT_PH_TARGET)
            ): vol.Coerce(float),
            vol.Optional(
                CONF_VPD_TARGET,
                default=current_config.get(CONF_VPD_TARGET, DEFAULT_VPD_TARGET)
            ): vol.Coerce(float),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
        )
