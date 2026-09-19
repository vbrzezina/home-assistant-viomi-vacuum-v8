"""Select entities for the Viomi Vacuum V8."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import BOX_TYPES, CLEANING_MODES, WATER_LEVELS
from .coordinator import ViomiDataUpdateCoordinator


class ViomiCleaningModeSelect(
    CoordinatorEntity[ViomiDataUpdateCoordinator],
    SelectEntity,
):
    """Select the cleaning mode."""

    _attr_icon = "mdi:vacuum"
    _attr_name = "Cleaning Mode"

    def __init__(
        self,
        coordinator: ViomiDataUpdateCoordinator,
    ) -> None:
        """Initialize the cleaning mode select."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.mac_address}_cleaning_mode"

    @property
    def options(self) -> list[str]:
        """Return the cleaning modes supported by the installed hardware."""
        data = self.coordinator.data

        box_type = int(data["box_type"])
        mop_installed = bool(data["mop_type"])

        if box_type == 1:
            # Vacuum bin.
            return [CLEANING_MODES[0]]

        if box_type == 2:
            # Water-only bin requires the mop attachment.
            if mop_installed:
                return [CLEANING_MODES[2]]
            return []

        if box_type == 3:
            # 2-in-1 bin.
            if mop_installed:
                return [
                    CLEANING_MODES[0],
                    CLEANING_MODES[1],
                    CLEANING_MODES[2],
                ]

            return [CLEANING_MODES[0]]

        # No bin / unknown bin.
        return []

    @property
    def current_option(self) -> str | None:
        """Return the currently selected cleaning mode."""
        mode = int(self.coordinator.data["is_mop"])
        option = CLEANING_MODES.get(mode)

        if option in self.options:
            return option

        return None

    async def async_select_option(self, option: str) -> None:
        """Set the cleaning mode."""
        mode = next(
            (
                value
                for value, name in CLEANING_MODES.items()
                if name == option
            ),
            None,
        )

        if mode is None or option not in self.options:
            raise ValueError(f"Unsupported cleaning mode: {option}")

        await self.hass.async_add_executor_job(
            self.coordinator.vacuum.raw_command,
            "set_mop",
            [mode],
        )

        await self.coordinator.async_request_refresh()


class ViomiWaterLevelSelect(
    CoordinatorEntity[ViomiDataUpdateCoordinator],
    SelectEntity,
):
    """Select the water level."""

    _attr_icon = "mdi:water"
    _attr_name = "Water Level"

    def __init__(
        self,
        coordinator: ViomiDataUpdateCoordinator,
    ) -> None:
        """Initialize the water level select."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.mac_address}_water_level"

    @property
    def available(self) -> bool:
        """Return whether water-level control is available."""
        box_type = int(self.coordinator.data["box_type"])

        return box_type in (2, 3)

    @property
    def options(self) -> list[str]:
        """Return available water levels."""
        return list(WATER_LEVELS)

    @property
    def current_option(self) -> str | None:
        """Return the currently selected water level."""
        value = int(self.coordinator.data["water_grade"])

        return next(
            (
                name
                for name, level in WATER_LEVELS.items()
                if level == value
            ),
            None,
        )

    async def async_select_option(self, option: str) -> None:
        """Set the water level."""
        if not self.available:
            raise ValueError("Water-level control is unavailable")

        level = WATER_LEVELS.get(option)

        if level is None:
            raise ValueError(f"Unsupported water level: {option}")

        await self.hass.async_add_executor_job(
            self.coordinator.vacuum.raw_command,
            "set_suction",
            [level],
        )

        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
) -> None:
    """Set up the Viomi Vacuum V8 select entities."""
    coordinator: ViomiDataUpdateCoordinator = entry.runtime_data

    async_add_entities(
        [
            ViomiCleaningModeSelect(coordinator),
            ViomiWaterLevelSelect(coordinator),
        ]
    )