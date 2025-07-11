"""Climate platform for NECTOR200."""
import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

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
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 0.1
    _attr_min_temp = -50.0  # Typical range for refrigeration
    _attr_max_temp = 50.0

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
        
        # Use the new async_set_temperature method
        success = await self.coordinator.async_set_temperature(temperature)
        
        if success:
            # Update the local data optimistically
            self.coordinator.data["setpoint"] = temperature
            self.async_write_ha_state()
            # Then request a refresh to get the actual value
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set temperature to %s", temperature)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode."""
        # Use the new async_set_standby method
        if hvac_mode == HVACMode.OFF:
            success = await self.coordinator.async_set_standby(True)
        else:
            success = await self.coordinator.async_set_standby(False)
        
        if success:
            # Update the local data optimistically
            self.coordinator.data["standby"] = (hvac_mode == HVACMode.OFF)
            self.async_write_ha_state()
            # Then request a refresh to get the actual value
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set HVAC mode to %s", hvac_mode)