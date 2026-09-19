"""Binary sensors for the Viomi Vacuum V8."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import voluptuous as vol
from homeassistant.components.binary_sensor import (
    PLATFORM_SCHEMA as BINARY_SENSOR_PLATFORM_SCHEMA,
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DEFAULT_NAME
from .coordinator import (
    ViomiDataUpdateCoordinator,
    async_get_coordinator,
)

PLATFORM_SCHEMA = BINARY_SENSOR_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_TOKEN): vol.All(
            cv.string,
            vol.Length(min=32, max=32),
        ),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

class ViomiBinarySensor(
    CoordinatorEntity[ViomiDataUpdateCoordinator],
    BinarySensorEntity,
):
    """Base Viomi binary sensor."""

    def __init__(
        self,
        coordinator: ViomiDataUpdateCoordinator,
        name: str,
        unique_suffix: str,
        key: str,
        transform: Callable[[Any], bool] | None = None,
        *,
        device_class: BinarySensorDeviceClass | None = None,
    ) -> None:
        """Initialize a binary sensor."""
        super().__init__(coordinator)

        self._key = key
        self._transform = transform

        self._attr_name = f"{name} {unique_suffix}"
        self._attr_unique_id = (
            f"{coordinator.mac_address}_"
            f"{unique_suffix.lower().replace(' ', '_')}"
        )
        self._attr_device_class = device_class

    @property
    def device_info(self) -> DeviceInfo:
        """Return information about the device."""
        return self.coordinator.device_info

    @property
    def is_on(self) -> bool | None:
        """Return whether the sensor is on."""
        if not self.coordinator.data:
            return None

        value = self.coordinator.data.get(self._key)

        if value is None:
            return None

        if self._transform is not None:
            return self._transform(value)

        return bool(value)

async def async_setup_platform(
    hass,
    config,
    async_add_entities,
    discovery_info=None,
):
    """Set up Viomi binary sensors."""
    coordinator = await async_get_coordinator(
        hass,
        config[CONF_HOST],
        config[CONF_TOKEN],
        config[CONF_NAME],
    )

    name = config[CONF_NAME]

    entities = [
        ViomiBinarySensor(
            coordinator,
            name,
            "Charging",
            "is_charge",
            device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        ),
        ViomiBinarySensor(
            coordinator,
            name,
            "Working",
            "is_work",
            device_class=BinarySensorDeviceClass.RUNNING,
        ),
        ViomiBinarySensor(
            coordinator,
            name,
            "Has Map",
            "has_map",
        ),
        ViomiBinarySensor(
            coordinator,
            name,
            "New Map",
            "has_newmap",
        ),
        ViomiBinarySensor(
            coordinator,
            name,
            "Mop Installed",
            "mop_type",
        ),
        ViomiBinarySensor(
            coordinator,
            name,
            "Remember Map",
            "remember_map",
        ),
        ViomiBinarySensor(
            coordinator,
            name,
            "Repeat Cleaning",
            "repeat_state",
        ),
        ViomiBinarySensor(
            coordinator,
            name,
            "Problem",
            "err_state",
            lambda value: int(value) != 0,
            device_class=BinarySensorDeviceClass.PROBLEM,
        ),
    ]

    async_add_entities(entities)