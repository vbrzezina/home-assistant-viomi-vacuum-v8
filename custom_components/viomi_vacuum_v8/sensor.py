"""Sensors for the Viomi Vacuum V8."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfArea,
    UnitOfTime,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    BOX_TYPES,
    FAN_SPEEDS,
)
from .coordinator import (
    ViomiDataUpdateCoordinator,
)

REVERSE_FAN_SPEEDS = {value: key for key, value in FAN_SPEEDS.items()}

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
        return self.coordinator.device_info

async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    """Set up Viomi sensors."""
    coordinator = entry.runtime_data
    name = coordinator.name

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
            options=[*FAN_SPEEDS.keys(), "Unknown"],
            icon="mdi:fan",
        ),
        ViomiSensor(
            coordinator,
            name,
            "Installed Box",
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