"""Sensor platform for NECTOR200."""
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
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
    """Set up NECTOR200 sensor entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = [
        NECTOR200TemperatureSensor(coordinator, config_entry),
        NECTOR200SetpointSensor(coordinator, config_entry),
        NECTOR200StatusSensor(coordinator, config_entry, "alarm", "Alarm"),
        NECTOR200StatusSensor(coordinator, config_entry, "recording", "Recording"),
    ]
    
    async_add_entities(entities)


class NECTOR200TemperatureSensor(CoordinatorEntity, SensorEntity):
    """Temperature sensor for NECTOR200."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, config_entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry.entry_id}_temperature"
        self._attr_name = "WH1 Temperature"

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        return self.coordinator.data.get("temperature")


class NECTOR200SetpointSensor(CoordinatorEntity, SensorEntity):
    """Setpoint sensor for NECTOR200."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, config_entry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry.entry_id}_setpoint"
        self._attr_name = "WH1 Setpoint"

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        return self.coordinator.data.get("setpoint")


class NECTOR200StatusSensor(CoordinatorEntity, SensorEntity):
    """Status sensor for NECTOR200."""

    def __init__(self, coordinator, config_entry, sensor_type: str, name: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_unique_id = f"{config_entry.entry_id}_{sensor_type}"
        self._attr_name = f"WH1 {name}"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        return "On" if self.coordinator.data.get(self._sensor_type) else "Off"