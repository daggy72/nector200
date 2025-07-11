"""Switch platform for NECTOR200."""
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    """Set up NECTOR200 switch entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = [
        NECTOR200LightSwitch(coordinator, config_entry),
        NECTOR200DefrostSwitch(coordinator, config_entry),
    ]
    
    async_add_entities(entities)


class NECTOR200LightSwitch(CoordinatorEntity, SwitchEntity):
    """Light switch entity for NECTOR200."""

    def __init__(self, coordinator, config_entry):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry.entry_id}_light"
        self._attr_name = "WH1 Light"

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self.coordinator.data.get("light", False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        # Only toggle if currently off
        if not self.is_on:
            success = await self.coordinator.async_toggle_light()
            if success:
                await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        # Only toggle if currently on
        if self.is_on:
            success = await self.coordinator.async_toggle_light()
            if success:
                await self.coordinator.async_request_refresh()


class NECTOR200DefrostSwitch(CoordinatorEntity, SwitchEntity):
    """Defrost switch entity for NECTOR200."""

    def __init__(self, coordinator, config_entry):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry.entry_id}_defrost"
        self._attr_name = "WH1 Defrost"

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self.coordinator.data.get("defrost", False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        # Only toggle if currently off
        if not self.is_on:
            success = await self.coordinator.async_toggle_defrost()
            if success:
                await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        # Only toggle if currently on
        if self.is_on:
            success = await self.coordinator.async_toggle_defrost()
            if success:
                await self.coordinator.async_request_refresh()