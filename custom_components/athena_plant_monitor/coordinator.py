"""Data update coordinator for Athena Plant Monitor."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers import entity_registry as er
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN

from .const import (
    DOMAIN,
    ESPHOME_ENTITIES,
    GROWTH_PHASES,
    CROP_STEERING_STRATEGIES,
    IRRIGATION_PHASES,
    ALERT_THRESHOLDS,
    CLIMATE_STRATEGIES,
    VENTILATION_MODES,
)

_LOGGER = logging.getLogger(__name__)


class AthenaPlantCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from ESPHome entities."""

    def __init__(self, hass: HomeAssistant, device_id: str, update_interval: int) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )
        self.device_id = device_id
        self._entity_ids = {}
        self._irrigation_state = {
            "current_phase": "P3",
            "last_irrigation": None,
            "daily_water_total": 0.0,
            "max_vwc_today": 0.0,
            "lights_on": False,
            "automation_enabled": True,
        }
        self._growth_config = {
            "phase": "vegetative",
            "steering": "vegetative", 
            "substrate_size": 10.0,
        }
        
        # Build entity ID mapping
        self._build_entity_mapping()

    def _build_entity_mapping(self) -> None:
        """Build mapping of logical names to actual entity IDs."""
        for key, pattern in ESPHOME_ENTITIES.items():
            entity_id = pattern.format(device_id=self.device_id)
            self._entity_ids[key] = entity_id

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from ESPHome entities."""
        try:
            data = {}
            
            # Fetch all sensor states
            for key, entity_id in self._entity_ids.items():
                state = self.hass.states.get(entity_id)
                if state and state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                    try:
                        # Try to convert to float for sensors
                        if key in ["temperature", "humidity", "vwc", "ec_substrate", "ph_substrate", 
                                  "temp_substrate", "co2", "light", "water_level", "pressure"]:
                            data[key] = float(state.state)
                        else:
                            data[key] = state.state
                    except (ValueError, TypeError):
                        data[key] = state.state
                else:
                    data[key] = None
                    
            # Calculate derived values
            data.update(self._calculate_derived_values(data))
            
            # Update irrigation state
            self._update_irrigation_state(data)
            
            # Check for alerts
            alerts = self._check_alerts(data)
            data["alerts"] = alerts
            
            # Add configuration
            data["growth_config"] = self._growth_config.copy()
            data["irrigation_state"] = self._irrigation_state.copy()
            
            return data
            
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            raise UpdateFailed(f"Error communicating with ESPHome devices: {err}")

    def _calculate_derived_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate VPD, dryback, and other derived values."""
        derived = {}
        
        # Basic VPD calculation (inside)
        temp = data.get("temperature")
        humidity = data.get("humidity")
        if temp is not None and humidity is not None:
            svp = 0.6108 * (2.71828 ** (17.27 * temp / (temp + 237.3)))
            derived["vpd_calculated"] = round((svp * (100 - humidity)) / 100, 2)
        
        # Outside VPD calculation
        temp_outside = data.get("temperature_outside")
        humidity_outside = data.get("humidity_outside")
        if temp_outside is not None and humidity_outside is not None:
            svp_outside = 0.6108 * (2.71828 ** (17.27 * temp_outside / (temp_outside + 237.3)))
            derived["vpd_outside"] = round((svp_outside * (100 - humidity_outside)) / 100, 2)
        
        # Climate differentials
        if temp is not None and temp_outside is not None:
            derived["temperature_differential"] = round(temp - temp_outside, 1)
        
        if humidity is not None and humidity_outside is not None:
            derived["humidity_differential"] = round(humidity - humidity_outside, 1)
        
        # VPD Target based on growth phase and time
        vpd_target = self._calculate_vpd_target()
        derived["vpd_target"] = vpd_target
        
        # Climate strategy recommendation
        climate_strategy = self._determine_climate_strategy(data, derived)
        derived["climate_strategy"] = climate_strategy["strategy"]
        derived["ventilation_recommendation"] = climate_strategy["ventilation"]
        
        # Dryback calculation
        current_vwc = data.get("vwc")
        max_vwc = self._irrigation_state.get("max_vwc_today", 0)
        if current_vwc is not None and max_vwc > 0:
            derived["dryback_percent"] = round(((max_vwc - current_vwc) / max_vwc) * 100, 1)
        else:
            derived["dryback_percent"] = 0
            
        # VWC Target
        derived["vwc_target"] = self._calculate_vwc_target()
        
        # EC and pH targets
        derived["ec_target"] = self._calculate_ec_target()
        derived["ph_target"] = self._calculate_ph_target()
        
        return derived

    def _calculate_vpd_target(self) -> float:
        """Calculate VPD target based on growth phase and lighting."""
        phase = self._growth_config["phase"]
        steering = self._growth_config["steering"]
        
        # Check if lights are on
        lights_on = self.hass.states.get(self._entity_ids.get("led_panel"))
        is_lights_on = lights_on and lights_on.state == "on"
        
        # Base VPD targets from Athena guidelines
        if phase == "vegetative":
            base_vpd = 0.9 if is_lights_on else 0.7
        elif phase in ["flowering_stretch", "flowering_bulk"]:
            base_vpd = 1.2 if is_lights_on else 0.9
        elif phase == "flowering_finish":
            base_vpd = 1.4 if is_lights_on else 1.0
        else:
            base_vpd = 1.0
            
        # Adjust for crop steering
        if steering == "generative":
            base_vpd += 0.2
        elif steering == "vegetative":
            base_vpd -= 0.1
            
        return round(max(0.5, min(2.0, base_vpd)), 2)

    def _determine_climate_strategy(self, data: Dict[str, Any], derived: Dict[str, Any]) -> Dict[str, str]:
        """Determine optimal climate strategy based on inside/outside conditions."""
        
        temp_in = data.get("temperature")
        humidity_in = data.get("humidity")
        vpd_in = derived.get("vpd_calculated")
        
        temp_out = data.get("temperature_outside")
        humidity_out = data.get("humidity_outside")
        vpd_out = derived.get("vpd_outside")
        
        vpd_target = derived.get("vpd_target", 1.0)
        
        # Default strategy
        strategy = "maintain"
        ventilation = "normal"
        
        if all(v is not None for v in [temp_in, humidity_in, vpd_in, temp_out, humidity_out, vpd_out]):
            
            # VPD too low (high humidity) - need dehumidification
            if vpd_in < vpd_target - 0.2:
                if temp_out > temp_in and humidity_out < humidity_in:
                    strategy = "intake_air"
                    ventilation = "increase_intake"
                elif temp_in < 28:  # Can still heat without stress
                    strategy = "heat_dehumidify"
                    ventilation = "increase_exhaust"
                else:
                    strategy = "dehumidify_only"
                    ventilation = "normal"
            
            # VPD too high (low humidity) - need humidification
            elif vpd_in > vpd_target + 0.2:
                if temp_out < temp_in and humidity_out > humidity_in:
                    strategy = "intake_air"
                    ventilation = "increase_intake"
                elif temp_in > 20:  # Can cool down
                    strategy = "cool_humidify"
                    ventilation = "increase_exhaust"
                else:
                    strategy = "humidify_only"
                    ventilation = "reduce_exhaust"
            
            # Temperature management
            elif temp_in > 28:  # Too hot
                if temp_out < temp_in - 2:
                    strategy = "cooling_ventilation"
                    ventilation = "maximum_intake"
                else:
                    strategy = "cooling_only"
                    ventilation = "increase_exhaust"
            
            elif temp_in < 20:  # Too cold
                strategy = "heating"
                ventilation = "reduce_intake"
            
            # Optimal conditions
            else:
                strategy = "maintain_optimal"
                ventilation = "normal"
        
        return {
            "strategy": strategy,
            "ventilation": ventilation
        }

    async def trigger_irrigation_shot(self, shot_size: float, duration: int) -> None:
        """Trigger a manual irrigation shot."""
        pump_entity = self._entity_ids.get("pump")
        if pump_entity:
            try:
                # Turn on pump
                await self.hass.services.async_call(
                    "switch", "turn_on",
                    {"entity_id": pump_entity}
                )
                
                # Wait for duration
                await asyncio.sleep(duration)
                
                # Turn off pump
                await self.hass.services.async_call(
                    "switch", "turn_off", 
                    {"entity_id": pump_entity}
                )
                
                # Update irrigation tracking
                self._irrigation_state["last_irrigation"] = datetime.now()
                water_amount = (shot_size / 100) * self._growth_config["substrate_size"]
                self._irrigation_state["daily_water_total"] += water_amount
                
                _LOGGER.info(f"Manual irrigation shot: {shot_size}% for {duration}s ({water_amount:.1f}L)")
                
                # Request data update
                await self.async_request_refresh()
                
            except Exception as err:
                _LOGGER.error(f"Error during irrigation shot: {err}")
                raise

    async def set_growth_phase(self, phase: str) -> None:
        """Set the growth phase."""
        if phase in GROWTH_PHASES:
            self._growth_config["phase"] = phase
            _LOGGER.info(f"Growth phase set to: {phase}")
            await self.async_request_refresh()

    async def set_crop_steering(self, strategy: str) -> None:
        """Set the crop steering strategy."""
        if strategy in CROP_STEERING_STRATEGIES:
            self._growth_config["steering"] = strategy
            _LOGGER.info(f"Crop steering set to: {strategy}")
            await self.async_request_refresh()

    async def apply_climate_strategy(self, strategy: str = None) -> None:
        """Apply climate control strategy based on current conditions."""
        if strategy is None:
            # Auto-determine strategy
            data = self.data or {}
            derived = self._calculate_derived_values(data)
            climate_strategy = self._determine_climate_strategy(data, derived)
            strategy = climate_strategy["strategy"]
        
        if strategy not in CLIMATE_STRATEGIES:
            _LOGGER.error(f"Unknown climate strategy: {strategy}")
            return
            
        strategy_config = CLIMATE_STRATEGIES[strategy]
        actions = strategy_config["actions"]
        
        _LOGGER.info(f"Applying climate strategy: {strategy} - {strategy_config['description']}")
        
        # Apply actions based on strategy
        for action in actions:
            await self._execute_climate_action(action)
    
    async def _execute_climate_action(self, action: str) -> None:
        """Execute a specific climate control action."""
        try:
            if action == "increase_intake":
                await self._set_fan_speed("intake", 80)
            elif action == "reduce_intake":
                await self._set_fan_speed("intake", 30)
            elif action == "increase_exhaust":
                await self._set_fan_speed("exhaust", 80)
            elif action == "reduce_exhaust":
                await self._set_fan_speed("exhaust", 40)
            elif action == "maximum_intake":
                await self._set_fan_speed("intake", 100)
            elif action == "increase_heating":
                # Could control heater if available
                _LOGGER.info("Heating increase recommended")
            elif action == "increase_dehumidifier":
                if self._entity_ids.get("dehumidifier"):
                    await self.hass.services.async_call(
                        "switch", "turn_on",
                        {"entity_id": self._entity_ids["dehumidifier"]}
                    )
            elif action == "increase_humidifier":
                if self._entity_ids.get("humidifier"):
                    await self.hass.services.async_call(
                        "switch", "turn_on", 
                        {"entity_id": self._entity_ids["humidifier"]}
                    )
            elif action == "increase_circulation":
                await self._set_fan_speed("circulation", 100)
            elif action == "monitor":
                _LOGGER.info("Monitoring - optimal conditions")
            elif action == "fine_tune":
                await self._fine_tune_climate()
        except Exception as err:
            _LOGGER.error(f"Error executing climate action {action}: {err}")
    
    async def _set_fan_speed(self, fan_type: str, speed: int) -> None:
        """Set fan speed (if variable speed control available)."""
        fan_entity = self._entity_ids.get(f"fan_{fan_type}")
        if fan_entity:
            # For simple on/off fans
            if speed > 50:
                await self.hass.services.async_call(
                    "switch", "turn_on",
                    {"entity_id": fan_entity}
                )
            else:
                await self.hass.services.async_call(
                    "switch", "turn_off",
                    {"entity_id": fan_entity}
                )
            _LOGGER.info(f"Set {fan_type} fan to {speed}%")
    
    async def _fine_tune_climate(self) -> None:
        """Fine-tune climate when in optimal range."""
        data = self.data or {}
        vpd_current = data.get("vpd_calculated")
        vpd_target = self._calculate_vpd_target()
        
        if vpd_current and vpd_target:
            diff = vpd_current - vpd_target
            if abs(diff) > 0.1:  # Only adjust if significant difference
                if diff > 0:  # VPD too high, need more humidity
                    if self._entity_ids.get("humidifier"):
                        await self.hass.services.async_call(
                            "switch", "turn_on",
                            {"entity_id": self._entity_ids["humidifier"]}
                        )
                else:  # VPD too low, need less humidity
                    if self._entity_ids.get("dehumidifier"):
                        await self.hass.services.async_call(
                            "switch", "turn_on", 
                            {"entity_id": self._entity_ids["dehumidifier"]}
                        )

    async def set_ventilation_mode(self, mode: str) -> None:
        """Set ventilation mode according to VENTILATION_MODES."""
        if mode not in VENTILATION_MODES:
            _LOGGER.error(f"Unknown ventilation mode: {mode}")
            return
            
        ventilation_config = VENTILATION_MODES[mode]
        _LOGGER.info(f"Setting ventilation mode: {mode} - {ventilation_config['description']}")
        
        # Set intake fan
        if "intake_fan" in ventilation_config:
            await self._set_fan_speed("intake", ventilation_config["intake_fan"])
        
        # Set exhaust fan  
        if "exhaust_fan" in ventilation_config:
            await self._set_fan_speed("exhaust", ventilation_config["exhaust_fan"])
            
        # Set circulation fan
        if "circulation_fan" in ventilation_config:
            await self._set_fan_speed("circulation", ventilation_config["circulation_fan"])

    async def optimize_vpd(self, target_vpd: float = None) -> None:
        """Optimize VPD using inside/outside climate conditions."""
        if target_vpd is None:
            target_vpd = self._calculate_vpd_target()
            
        data = self.data or {}
        vpd_current = data.get("vpd_calculated")
        vpd_outside = data.get("vpd_outside") 
        temp_in = data.get("temperature")
        temp_out = data.get("temperature_outside")
        humidity_in = data.get("humidity")
        humidity_out = data.get("humidity_outside")
        
        if not all(v is not None for v in [vpd_current, target_vpd]):
            _LOGGER.warning("Insufficient data for VPD optimization")
            return
            
        vpd_diff = vpd_current - target_vpd
        _LOGGER.info(f"VPD optimization: Current {vpd_current}, Target {target_vpd}, Diff {vpd_diff}")
        
        # Strategy based on VPD difference and outside conditions
        if abs(vpd_diff) < 0.1:
            # Already optimal
            await self.apply_climate_strategy("maintain_optimal")
        elif vpd_diff < -0.2:  # VPD too low (too humid)
            if vpd_outside and vpd_outside > vpd_current and temp_out and temp_in:
                if temp_out <= temp_in + 2:  # Outside temp acceptable
                    await self.apply_climate_strategy("intake_air")
                else:
                    await self.apply_climate_strategy("dehumidify_only")
            else:
                await self.apply_climate_strategy("heat_dehumidify")
        elif vpd_diff > 0.2:  # VPD too high (too dry)
            if vpd_outside and vpd_outside < vpd_current and temp_out and temp_in:
                if temp_out >= temp_in - 2:  # Outside temp acceptable
                    await self.apply_climate_strategy("intake_air")
                else:
                    await self.apply_climate_strategy("humidify_only")
            else:
                await self.apply_climate_strategy("cool_humidify")
