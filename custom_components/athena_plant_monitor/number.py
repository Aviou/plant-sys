"""Number platform for Athena Plant Monitor."""
import logging
from typing import Any, Dict, Optional

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DATA_COORDINATOR
from .coordinator import AthenaPlantCoordinator

_LOGGER = logging.getLogger(__name__)

NUMBER_DESCRIPTIONS = [
    NumberEntityDescription(
        key="substrate_size",
        name="Substratgröße",
        icon="mdi:cube-outline",
        native_min_value=1.0,
        native_max_value=50.0,
        native_step=0.5,
        native_unit_of_measurement="L",
        mode=NumberMode.BOX,
    ),
    NumberEntityDescription(
        key="vwc_target_manual",
        name="VWC Zielwert (Manuell)",
        icon="mdi:bullseye-arrow",
        native_min_value=40.0,
        native_max_value=95.0,
        native_step=1.0,
        native_unit_of_measurement="%",
        mode=NumberMode.SLIDER,
    ),
    NumberEntityDescription(
        key="ec_target_manual",
        name="EC Zielwert (Manuell)",
        icon="mdi:bullseye-arrow",
        native_min_value=1.0,
        native_max_value=12.0,
        native_step=0.1,
        native_unit_of_measurement="ppm",
        mode=NumberMode.BOX,
    ),
    NumberEntityDescription(
        key="ph_target_manual",
        name="pH Zielwert (Manuell)",
        icon="mdi:bullseye-arrow",
        native_min_value=5.0,
        native_max_value=7.5,
        native_step=0.1,
        mode=NumberMode.BOX,
    ),
    NumberEntityDescription(
        key="vpd_target_manual",
        name="VPD Zielwert (Manuell)",
        icon="mdi:bullseye-arrow",
        native_min_value=0.5,
        native_max_value=2.0,
        native_step=0.1,
        native_unit_of_measurement="kPa",
        mode=NumberMode.BOX,
    ),
    NumberEntityDescription(
        key="irrigation_shot_size",
        name="Bewässerungsschuss Größe",
        icon="mdi:water-percent",
        native_min_value=1.0,
        native_max_value=10.0,
        native_step=0.5,
        native_unit_of_measurement="%",
        mode=NumberMode.SLIDER,
    ),
    NumberEntityDescription(
        key="irrigation_duration",
        name="Bewässerungsdauer",
        icon="mdi:timer",
        native_min_value=5,
        native_max_value=300,
        native_step=5,
        native_unit_of_measurement="s",
        mode=NumberMode.BOX,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_COORDINATOR]

    entities = []
    for description in NUMBER_DESCRIPTIONS:
        entities.append(AthenaPlantNumber(coordinator, description))

    async_add_entities(entities)


class AthenaPlantNumber(CoordinatorEntity, NumberEntity):
    """Representation of an Athena Plant Monitor number entity."""

    def __init__(
        self,
        coordinator: AthenaPlantCoordinator,
        description: NumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device_id}_number_{description.key}"
        self._attr_device_info = coordinator.device_info
        
        # Set default values
        self._values = {
            "substrate_size": 10.0,
            "vwc_target_manual": 75.0,
            "ec_target_manual": 4.0,
            "ph_target_manual": 6.0,
            "vpd_target_manual": 1.0,
            "irrigation_shot_size": 3.0,
            "irrigation_duration": 30,
        }

    @property
    def native_value(self) -> Optional[float]:
        """Return the current value."""
        key = self.entity_description.key
        
        if key == "substrate_size":
            return self.coordinator._growth_config.get("substrate_size", 10.0)
        else:
            return self._values.get(key, self.entity_description.native_min_value)

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        key = self.entity_description.key
        
        if key == "substrate_size":
            self.coordinator._growth_config["substrate_size"] = value
            await self.coordinator.async_request_refresh()
        else:
            self._values[key] = value
        
        # Trigger update
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        key = self.entity_description.key
        
        # Add context based on entity type
        if key.endswith("_target_manual"):
            # For manual targets, show auto-calculated target for comparison
            base_key = key.replace("_target_manual", "_target")
            auto_target = self.coordinator.data.get(base_key)
            if auto_target is not None:
                attrs["auto_calculated_target"] = auto_target
                attrs["deviation_from_auto"] = round(self.native_value - auto_target, 2) if self.native_value else 0
        
        elif key == "substrate_size":
            # Show impact on irrigation calculations
            daily_water = self.coordinator.data.get("irrigation_state", {}).get("daily_water_total", 0)
            if daily_water > 0:
                attrs["daily_water_percent"] = round((daily_water / self.native_value) * 100, 1) if self.native_value else 0
        
        elif key in ["irrigation_shot_size", "irrigation_duration"]:
            # Show calculated water amount
            substrate_size = self.coordinator._growth_config.get("substrate_size", 10.0)
            if key == "irrigation_shot_size":
                water_amount = (self.native_value / 100) * substrate_size if self.native_value else 0
                attrs["water_amount_liters"] = round(water_amount, 2)
        
        # Add growth context
        growth_config = self.coordinator.data.get("growth_config", {})
        attrs.update({
            "growth_phase": growth_config.get("phase"),
            "crop_steering": growth_config.get("steering"),
        })
        
        return attrs
