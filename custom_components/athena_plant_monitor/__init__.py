"""
Athena Plant Monitor Integration für Home Assistant.

Ein fortschrittliches System zur Überwachung und Steuerung von Pflanzen
basierend auf den Athena® Standards mit ESPHome Integration.
"""
import asyncio
import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity_registry import async_get
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    PLATFORMS,
    DEFAULT_UPDATE_INTERVAL,
    CONF_DEVICE_ID,
    CONF_UPDATE_INTERVAL,
    CONF_GROWTH_PHASE,
    CONF_CROP_STEERING,
    CONF_SUBSTRATE_SIZE,
    DATA_COORDINATOR,
    DATA_CONFIG,
)
from .coordinator import AthenaPlantCoordinator

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): vol.Coerce(int),
                vol.Optional(CONF_GROWTH_PHASE, default="vegetative"): vol.In([
                    "vegetative", "flowering_stretch", "flowering_bulk", "flowering_finish"
                ]),
                vol.Optional(CONF_CROP_STEERING, default="vegetative"): vol.In([
                    "vegetative", "generative", "balanced"
                ]),
                vol.Optional(CONF_SUBSTRATE_SIZE, default=10): vol.Coerce(float),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Athena Plant Monitor integration."""
    hass.data.setdefault(DOMAIN, {})
    
    if DOMAIN in config:
        hass.data[DOMAIN][DATA_CONFIG] = config[DOMAIN]
    
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Athena Plant Monitor from a config entry."""
    _LOGGER.info("Setting up Athena Plant Monitor integration")
    
    # Store config data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}
    
    # Create coordinator
    coordinator = AthenaPlantCoordinator(
        hass,
        entry.data.get(CONF_DEVICE_ID, "esphome_node_1"),
        entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
    )
    
    # Store coordinator
    hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR] = coordinator
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    # Forward the setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register services
    await _async_register_services(hass, coordinator)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading Athena Plant Monitor integration")
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


async def _async_register_services(hass: HomeAssistant, coordinator: AthenaPlantCoordinator) -> None:
    """Register integration services."""
    
    async def handle_irrigation_shot(call):
        """Handle manual irrigation shot service."""
        shot_size = call.data.get("shot_size", 3.0)  # Default 3% shot
        duration = call.data.get("duration", 30)  # Default 30 seconds
        
        await coordinator.trigger_irrigation_shot(shot_size, duration)
        
    async def handle_set_growth_phase(call):
        """Handle set growth phase service."""
        phase = call.data.get("phase")
        await coordinator.set_growth_phase(phase)
        
    async def handle_set_crop_steering(call):
        """Handle set crop steering service."""
        strategy = call.data.get("strategy")
        await coordinator.set_crop_steering(strategy)
        
    # Register services
    hass.services.async_register(
        DOMAIN,
        "irrigation_shot",
        handle_irrigation_shot,
        schema=vol.Schema({
            vol.Optional("shot_size", default=3.0): vol.Coerce(float),
            vol.Optional("duration", default=30): vol.Coerce(int),
        }),
    )
    
    hass.services.async_register(
        DOMAIN,
        "set_growth_phase",
        handle_set_growth_phase,
        schema=vol.Schema({
            vol.Required("phase"): vol.In([
                "vegetative", "flowering_stretch", "flowering_bulk", "flowering_finish"
            ]),
        }),
    )
    
    hass.services.async_register(
        DOMAIN,
        "set_crop_steering",
        handle_set_crop_steering,
        schema=vol.Schema({
            vol.Required("strategy"): vol.In([
                "vegetative", "generative", "balanced"
            ]),
        }),
    )
    
    # Climate control services
    async def handle_apply_climate_strategy(call):
        """Handle apply climate strategy service."""
        strategy = call.data.get("strategy")
        await coordinator.apply_climate_strategy(strategy)
        
    async def handle_set_ventilation_mode(call):
        """Handle set ventilation mode service."""
        mode = call.data.get("mode")
        await coordinator.set_ventilation_mode(mode)
        
    async def handle_optimize_vpd(call):
        """Handle optimize VPD service."""
        target_vpd = call.data.get("target_vpd")
        await coordinator.optimize_vpd(target_vpd)
    
    hass.services.async_register(
        DOMAIN,
        "apply_climate_strategy",
        handle_apply_climate_strategy,
        schema=vol.Schema({
            vol.Optional("strategy"): vol.In([
                "maintain_optimal", "intake_air", "heat_dehumidify", 
                "cool_humidify", "dehumidify_only", "humidify_only",
                "cooling_ventilation", "cooling_only", "heating"
            ]),
        }),
    )
    
    hass.services.async_register(
        DOMAIN,
        "set_ventilation_mode",
        handle_set_ventilation_mode,
        schema=vol.Schema({
            vol.Required("mode"): vol.In([
                "reduce_intake", "normal", "increase_intake",
                "increase_exhaust", "maximum_intake", "reduce_exhaust"
            ]),
        }),
    )
    
    hass.services.async_register(
        DOMAIN,
        "optimize_vpd",
        handle_optimize_vpd,
        schema=vol.Schema({
            vol.Optional("target_vpd"): vol.All(vol.Coerce(float), vol.Range(min=0.5, max=2.0)),
        }),
    )
