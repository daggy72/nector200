"""Climate platform for NECTOR200."""
import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, PARAM_SETPOINT

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NECTOR200 climate entity."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([NECTOR200Climate(coordinator, config_entry)])


class NECTOR200Climate(CoordinatorEntity, ClimateEntity):
    """Climate entity for NECTOR200."""

    _attr_hvac_modes = [HVACMode.COOL, HVACMode.OFF]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_temperature_unit = TEMP_CELSIUS
    _attr_target_temperature_step = 0.1

    def __init__(self, coordinator, config_entry):
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry.entry_id}_climate"
        self._attr_name = "WH1 Temperature Control"

    @property
    def current_temperature(self) -> float:
        """Return the current temperature."""
        return self.coordinator.data.get("temperature")

    @property
    def target_temperature(self) -> float:
        """Return the temperature we try to reach."""
        return self.coordinator.data.get("setpoint")

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        if self.coordinator.data.get("standby"):
            return HVACMode.OFF
        return HVACMode.COOL

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        
        # Send the setpoint to the device
        success = await self.coordinator.async_set_parameter(
            PARAM_SETPOINT, 
            str(temperature)
        )
        
        if success:
            await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode."""
        if hvac_mode == HVACMode.OFF:
            success = await self.coordinator.async_set_parameter(PARAM_STANDBY, "1")
        else:
            success = await self.coordinator.async_set_parameter(PARAM_STANDBY, "0")
        
        if success:
            await self.coordinator.async_request_refresh()