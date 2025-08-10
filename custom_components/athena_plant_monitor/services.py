"""Services for Athena Plant Monitor."""
import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, GROWTH_PHASES, CROP_STEERING_STRATEGIES, VENTILATION_MODES

_LOGGER = logging.getLogger(__name__)

# Service schemas
IRRIGATION_SHOT_SCHEMA = vol.Schema({
    vol.Optional("shot_size", default=3.0): vol.Coerce(float),
    vol.Optional("duration", default=30): vol.Coerce(int),
    vol.Optional("device_id"): cv.string,
})

SET_GROWTH_PHASE_SCHEMA = vol.Schema({
    vol.Required("phase"): vol.In(list(GROWTH_PHASES.keys())),
    vol.Optional("device_id"): cv.string,
})

SET_CROP_STEERING_SCHEMA = vol.Schema({
    vol.Required("strategy"): vol.In(list(CROP_STEERING_STRATEGIES.keys())),
    vol.Optional("device_id"): cv.string,
})

RESET_COUNTERS_SCHEMA = vol.Schema({
    vol.Optional("reset_water", default=False): cv.boolean,
    vol.Optional("reset_vwc", default=False): cv.boolean,
    vol.Optional("device_id"): cv.string,
})

EMERGENCY_PROTOCOL_SCHEMA = vol.Schema({
    vol.Optional("disable_automation", default=True): cv.boolean,
    vol.Optional("stop_all_pumps", default=True): cv.boolean,
    vol.Optional("device_id"): cv.string,
})

P1_SATURATION_SCHEMA = vol.Schema({
    vol.Optional("shot_count", default=3): vol.Coerce(int),
    vol.Optional("shot_size", default=4.0): vol.Coerce(float),
    vol.Optional("interval_minutes", default=20): vol.Coerce(int),
    vol.Optional("device_id"): cv.string,
})

APPLY_CLIMATE_STRATEGY_SCHEMA = vol.Schema({
    vol.Required("strategy"): cv.string,
    vol.Optional("device_id"): cv.string,
})

SET_VENTILATION_MODE_SCHEMA = vol.Schema({
    vol.Required("mode"): vol.In(VENTILATION_MODES),
    vol.Optional("device_id"): cv.string,
})

OPTIMIZE_VPD_SCHEMA = vol.Schema({
    vol.Required("target_vpd"): vol.Coerce(float),
    vol.Optional("device_id"): cv.string,
})


def get_coordinator_for_device(hass: HomeAssistant, device_id: str = None):
    """Get coordinator for specific device or first available."""
    domain_data = hass.data.get(DOMAIN, {})
    
    if device_id:
        # Look for specific device
        for entry_id, entry_data in domain_data.items():
            if entry_id == "config":
                continue
            coordinator = entry_data.get("coordinator")
            if coordinator and coordinator.device_id == device_id:
                return coordinator
    else:
        # Return first available coordinator
        for entry_id, entry_data in domain_data.items():
            if entry_id == "config":
                continue
            coordinator = entry_data.get("coordinator")
            if coordinator:
                return coordinator
    
    return None


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Athena Plant Monitor."""

    async def handle_irrigation_shot(call: ServiceCall) -> None:
        """Handle irrigation shot service."""
        device_id = call.data.get("device_id")
        coordinator = get_coordinator_for_device(hass, device_id)
        
        if not coordinator:
            _LOGGER.error("No coordinator found for irrigation shot service")
            return
            
        shot_size = call.data.get("shot_size", 3.0)
        duration = call.data.get("duration", 30)
        
        try:
            await coordinator.trigger_irrigation_shot(shot_size, duration)
            _LOGGER.info(f"Manual irrigation shot executed: {shot_size}% for {duration}s")
        except Exception as err:
            _LOGGER.error(f"Error executing irrigation shot: {err}")

    async def handle_set_growth_phase(call: ServiceCall) -> None:
        """Handle set growth phase service."""
        device_id = call.data.get("device_id")
        coordinator = get_coordinator_for_device(hass, device_id)
        
        if not coordinator:
            _LOGGER.error("No coordinator found for growth phase service")
            return
            
        phase = call.data.get("phase")
        
        try:
            await coordinator.set_growth_phase(phase)
            _LOGGER.info(f"Growth phase set to: {phase}")
        except Exception as err:
            _LOGGER.error(f"Error setting growth phase: {err}")

    async def handle_set_crop_steering(call: ServiceCall) -> None:
        """Handle set crop steering service."""
        device_id = call.data.get("device_id")
        coordinator = get_coordinator_for_device(hass, device_id)
        
        if not coordinator:
            _LOGGER.error("No coordinator found for crop steering service")
            return
            
        strategy = call.data.get("strategy")
        
        try:
            await coordinator.set_crop_steering(strategy)
            _LOGGER.info(f"Crop steering set to: {strategy}")
        except Exception as err:
            _LOGGER.error(f"Error setting crop steering: {err}")

    async def handle_reset_counters(call: ServiceCall) -> None:
        """Handle reset counters service."""
        device_id = call.data.get("device_id")
        coordinator = get_coordinator_for_device(hass, device_id)
        
        if not coordinator:
            _LOGGER.error("No coordinator found for reset counters service")
            return
            
        reset_water = call.data.get("reset_water", False)
        reset_vwc = call.data.get("reset_vwc", False)
        
        try:
            if reset_water:
                coordinator._irrigation_state["daily_water_total"] = 0.0
                _LOGGER.info("Daily water counter reset")
                
            if reset_vwc:
                coordinator._irrigation_state["max_vwc_today"] = 0.0
                _LOGGER.info("Max VWC counter reset")
                
            await coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(f"Error resetting counters: {err}")

    async def handle_emergency_protocol(call: ServiceCall) -> None:
        """Handle emergency protocol service."""
        device_id = call.data.get("device_id")
        coordinator = get_coordinator_for_device(hass, device_id)
        
        if not coordinator:
            _LOGGER.error("No coordinator found for emergency protocol service")
            return
            
        disable_automation = call.data.get("disable_automation", True)
        stop_all_pumps = call.data.get("stop_all_pumps", True)
        
        try:
            if disable_automation:
                coordinator._irrigation_state["automation_enabled"] = False
                _LOGGER.warning("Automation disabled by emergency protocol")
                
            if stop_all_pumps:
                pump_entity = coordinator.get_entity_id("pump")
                if pump_entity:
                    await hass.services.async_call(
                        "switch", "turn_off",
                        {"entity_id": pump_entity}
                    )
                _LOGGER.warning("All pumps stopped by emergency protocol")
                
            await coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(f"Error executing emergency protocol: {err}")

    async def handle_p1_saturation(call: ServiceCall) -> None:
        """Handle P1 saturation sequence service."""
        device_id = call.data.get("device_id")
        coordinator = get_coordinator_for_device(hass, device_id)
        
        if not coordinator:
            _LOGGER.error("No coordinator found for P1 saturation service")
            return
            
        shot_count = call.data.get("shot_count", 3)
        shot_size = call.data.get("shot_size", 4.0)
        interval_minutes = call.data.get("interval_minutes", 20)
        
        try:
            _LOGGER.info(f"Starting P1 saturation: {shot_count} shots of {shot_size}% every {interval_minutes} minutes")
            
            for i in range(shot_count):
                if i > 0:
                    # Wait between shots
                    import asyncio
                    await asyncio.sleep(interval_minutes * 60)
                
                # Execute shot
                duration = int(30 * (shot_size / 3.0))  # Scale duration with shot size
                await coordinator.trigger_irrigation_shot(shot_size, duration)
                _LOGGER.info(f"P1 saturation shot {i+1}/{shot_count} completed")
                
        except Exception as err:
            _LOGGER.error(f"Error executing P1 saturation: {err}")

    async def handle_apply_climate_strategy(call: ServiceCall) -> None:
        """Handle apply climate strategy service."""
        device_id = call.data.get("device_id")
        coordinator = get_coordinator_for_device(hass, device_id)
        
        if not coordinator:
            _LOGGER.error("No coordinator found for apply climate strategy service")
            return
            
        strategy = call.data.get("strategy")
        
        try:
            await coordinator.apply_climate_strategy(strategy)
            _LOGGER.info(f"Climate strategy applied: {strategy}")
        except Exception as err:
            _LOGGER.error(f"Error applying climate strategy: {err}")

    async def handle_set_ventilation_mode(call: ServiceCall) -> None:
        """Handle set ventilation mode service."""
        device_id = call.data.get("device_id")
        coordinator = get_coordinator_for_device(hass, device_id)
        
        if not coordinator:
            _LOGGER.error("No coordinator found for set ventilation mode service")
            return
            
        mode = call.data.get("mode")
        
        try:
            await coordinator.set_ventilation_mode(mode)
            _LOGGER.info(f"Ventilation mode set to: {mode}")
        except Exception as err:
            _LOGGER.error(f"Error setting ventilation mode: {err}")

    async def handle_optimize_vpd(call: ServiceCall) -> None:
        """Handle optimize VPD service."""
        device_id = call.data.get("device_id")
        coordinator = get_coordinator_for_device(hass, device_id)
        
        if not coordinator:
            _LOGGER.error("No coordinator found for optimize VPD service")
            return
            
        target_vpd = call.data.get("target_vpd")
        
        try:
            await coordinator.optimize_vpd(target_vpd)
            _LOGGER.info(f"VPD optimization started: target VPD = {target_vpd}")
        except Exception as err:
            _LOGGER.error(f"Error optimizing VPD: {err}")

    # Register services
    hass.services.async_register(
        DOMAIN,
        "irrigation_shot",
        handle_irrigation_shot,
        schema=IRRIGATION_SHOT_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        "set_growth_phase",
        handle_set_growth_phase,
        schema=SET_GROWTH_PHASE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        "set_crop_steering",
        handle_set_crop_steering,
        schema=SET_CROP_STEERING_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        "reset_counters",
        handle_reset_counters,
        schema=RESET_COUNTERS_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        "emergency_protocol",
        handle_emergency_protocol,
        schema=EMERGENCY_PROTOCOL_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        "p1_saturation_sequence",
        handle_p1_saturation,
        schema=P1_SATURATION_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        "apply_climate_strategy",
        handle_apply_climate_strategy,
        schema=APPLY_CLIMATE_STRATEGY_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        "set_ventilation_mode",
        handle_set_ventilation_mode,
        schema=SET_VENTILATION_MODE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        "optimize_vpd",
        handle_optimize_vpd,
        schema=OPTIMIZE_VPD_SCHEMA,
    )


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload services."""
    services = [
        "irrigation_shot",
        "set_growth_phase", 
        "set_crop_steering",
        "reset_counters",
        "emergency_protocol",
        "p1_saturation_sequence",
        "apply_climate_strategy",
        "set_ventilation_mode",
        "optimize_vpd",
    ]
    
    for service in services:
        hass.services.async_remove(DOMAIN, service)
