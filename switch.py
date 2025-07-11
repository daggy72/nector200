"""Switch platform for NECTOR200."""
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, PARAM_LIGHT, PARAM_DEFROST

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NECTOR200 switch entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = [
        NECTOR200Switch(coordinator, config_entry, "light", "Light", PARAM_LIGHT),
        NECTOR200Switch(coordinator, config_entry, "defrost", "Defrost", PARAM_DEFROST),
    ]
    
    async_add_entities(entities)


class NECTOR200Switch(CoordinatorEntity, SwitchEntity):
    """Switch entity for NECTOR200."""

    def __init__(self, coordinator, config_entry, switch_type: str, name: str, param: str):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._switch_type = switch_type
        self._param = param
        self._attr_unique_id = f"{config_entry.entry_id}_{switch_type}"
        self._attr_name = f"WH1 {name}"

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self.coordinator.data.get(self._switch_type, False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        success = await self.coordinator.async_set_parameter(self._param, "1")
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        success = await self.coordinator.async_set_parameter(self._param, "0")
        if success:
            await self.coordinator.async_request_refresh()