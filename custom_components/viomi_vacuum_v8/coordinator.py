"""Data update coordinator for the Viomi Vacuum V8."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from miio import DeviceException, ViomiVacuum  # pylint: disable=import-error
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    ALL_PROPS,
    DATA_KEY,
    VACUUM_CARD_PROPS_REFERENCES,
)

_LOGGER = logging.getLogger(__name__)


class ViomiDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate updates for one Viomi vacuum."""

    def __init__(
        self,
        hass: HomeAssistant,
        vacuum: ViomiVacuum,
        name: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(seconds=20),
            always_update=False,
        )

        self.vacuum = vacuum
        self.name = name
        self.mac_address: str | None = None
        self.firmware_version: str | None = None
        self.hardware_version: str | None = None
        self.model: str | None = None
        self.vacuum_entity = None

    def _fetch_state(self) -> dict[str, Any]:
        """Fetch and normalize vacuum state."""
        state = self.vacuum.raw_command("get_prop", ALL_PROPS)

        data = dict(zip(ALL_PROPS, state))

        for target, source in VACUUM_CARD_PROPS_REFERENCES.items():
            data[target] = data[source]

        return data

    def _update(self) -> dict[str, Any]:
        """Fetch state and keep the mop mode synchronized with the installed bin."""
        data = self._fetch_state()

        current_mode = int(data["is_mop"])
        box_type = int(data["box_type"])
        has_mop = bool(data["mop_type"])

        new_mode = None

        # 3 = 2-in-1 box
        if box_type == 3:
            if has_mop:
                new_mode = 1
            else:
                new_mode = 0

        # 2 = water-only box
        elif box_type == 2:
            new_mode = 2

        # 1 = dust-only box
        elif box_type == 1:
            new_mode = 0

        if new_mode is not None and new_mode != current_mode:
            self.vacuum.raw_command("set_mop", [new_mode])

            # Fetch the state again so the entities see the actual mode.
            data = self._fetch_state()

        return data

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the vacuum."""
        try:
            return await self.hass.async_add_executor_job(self._update)
        except (OSError, DeviceException) as err:
            raise UpdateFailed(f"Unable to update Viomi vacuum: {err}") from err


async def async_get_coordinator(
    hass: HomeAssistant,
    host: str,
    token: str,
    name: str,
) -> ViomiDataUpdateCoordinator:
    """Return the shared coordinator for a vacuum."""
    coordinators = hass.data.setdefault(DATA_KEY, {})

    if host in coordinators:
        return coordinators[host]

    _LOGGER.info("Initializing Viomi vacuum at %s", host)

    vacuum = ViomiVacuum(host, token)

    # We use the device MAC as the stable entity identifier.
    info = await hass.async_add_executor_job(vacuum.info)

    if not info.mac_address:
        raise DeviceException("Viomi vacuum did not report a MAC address")

    coordinator = ViomiDataUpdateCoordinator(hass, vacuum, name)

    coordinator.mac_address = info.mac_address.lower()
    coordinator.firmware_version = info.firmware_version
    coordinator.hardware_version = info.hardware_version
    coordinator.model = info.model

    coordinators[host] = coordinator

    # Initial update. Unlike async_config_entry_first_refresh(), this is
    # appropriate while this release still uses YAML platforms.
    await coordinator.async_refresh()

    return coordinator