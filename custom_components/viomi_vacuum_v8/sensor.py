"""Sensors for the Viomi Vacuum V8."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import voluptuous as vol
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_TOKEN,
    PERCENTAGE,
    UnitOfArea,
    UnitOfTime,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    BOX_TYPES,
    CLEANING_MODES,
    DEFAULT_NAME,
    FAN_SPEEDS,
    WATER_LEVELS,
)
from .coordinator import (
    ViomiDataUpdateCoordinator,
    async_get_coordinator,
)

PLATFORM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_TOKEN): vol.All(
            cv.string,
            vol.Length(min=32, max=32),
        ),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

REVERSE_FAN_SPEEDS = {value: key for key, value in FAN_SPEEDS.items()}
REVERSE_WATER_LEVELS = {value: key for key, value in WATER_LEVELS.items()}


class ViomiSensor(
    CoordinatorEntity[ViomiDataUpdateCoordinator],
    SensorEntity,
):
    """Base Viomi sensor."""

    def __init__(
        self,
        coordinator: ViomiDataUpdateCoordinator,
        name: str,
        unique_suffix: str,
        key: str,
        transform: Callable[[Any], Any] | None = None,
        *,
        device_class: SensorDeviceClass | None = None,
        unit: str | None = None,
        state_class: SensorStateClass | None = None,
        icon: str | None = None,
        options: list[str] | None = None,
    ) -> None:
        """Initialize a sensor."""
        super().__init__(coordinator)

        self._key = key
        self._transform = transform

        self._attr_name = f"{name} {unique_suffix}"
        self._attr_unique_id = f"{coordinator.mac_address}_{unique_suffix.lower().replace(' ', '_')}"

        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = state_class
        self._attr_icon = icon
        self._attr_options = options

    @property
    def native_value(self) -> Any:
        """Return the current value."""
        if not self.coordinator.data:
            return None

        value = self.coordinator.data.get(self._key)

        if self._transform is not None:
            return self._transform(value)

        return value

    @property
    def device_info(self) -> DeviceInfo:
        """Return information about the device."""
        return DeviceInfo(
            identifiers={
                ("viomi_vacuum_v8", self.coordinator.mac_address)
            },
            name=self.coordinator.name,
            manufacturer="Viomi",
            model="STYJ02YM",
        )

async def async_setup_platform(
    hass,
    config,
    async_add_entities,
    discovery_info=None,
):
    """Set up Viomi sensors."""
    coordinator = await async_get_coordinator(
        hass,
        config[CONF_HOST],
        config[CONF_TOKEN],
        config[CONF_NAME],
    )

    name = config[CONF_NAME]

    entities = [
        ViomiSensor(
            coordinator,
            name,
            "Battery",
            "battary_life",
            device_class=SensorDeviceClass.BATTERY,
            unit=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:battery",
        ),
        ViomiSensor(
            coordinator,
            name,
            "Cleaning Time",
            "s_time",
            lambda value: None if value is None else int(value) * 60,
            device_class=SensorDeviceClass.DURATION,
            unit=UnitOfTime.SECONDS,
            icon="mdi:timer-outline",
        ),
        ViomiSensor(
            coordinator,
            name,
            "Cleaned Area",
            "s_area",
            device_class=SensorDeviceClass.AREA,
            unit=UnitOfArea.SQUARE_METERS,
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:texture-box",
        ),
        ViomiSensor(
            coordinator,
            name,
            "Suction Power",
            "suction_grade",
            lambda value: REVERSE_FAN_SPEEDS.get(value, "Unknown"),
            device_class=SensorDeviceClass.ENUM,
            options=[*FAN_SPEEDS.values(), "Unknown"],
            icon="mdi:fan",
        ),
        ViomiSensor(
            coordinator,
            name,
            "Water Level",
            "water_grade",
            lambda value: REVERSE_WATER_LEVELS.get(value, "Unknown"),
            device_class=SensorDeviceClass.ENUM,
            options=[*WATER_LEVELS.values(), "Unknown"],
            icon="mdi:water",
        ),
        ViomiSensor(
            coordinator,
            name,
            "Cleaning Mode",
            "is_mop",
            lambda value: CLEANING_MODES.get(value, "Unknown"),
            device_class=SensorDeviceClass.ENUM,
            options=[*CLEANING_MODES.values(), "Unknown"],
            icon="mdi:robot-vacuum",
        ),
        ViomiSensor(
            coordinator,
            name,
            "Box Type",
            "box_type",
            lambda value: BOX_TYPES.get(value, "Unknown"),
            device_class=SensorDeviceClass.ENUM,
            options=[*BOX_TYPES.values(), "Unknown"],
            icon="mdi:inbox",
        ),
        ViomiSensor(
            coordinator,
            name,
            "Error Code",
            "err_state",
            icon="mdi:alert-circle-outline",
        ),
        ViomiSensor(
            coordinator,
            name,
            "Firmware",
            "sw_info",
            icon="mdi:chip",
        ),
        ViomiSensor(
            coordinator,
            name,
            "Hardware",
            "hw_info",
            icon="mdi:memory",
        ),
    ]

    async_add_entities(entities)