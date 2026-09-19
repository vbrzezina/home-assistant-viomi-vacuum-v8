"""Support for the Viomi Vacuum V8 robot."""
from functools import partial

import logging
import asyncio
import voluptuous as vol

from miio import DeviceException  # pylint: disable=import-error

from homeassistant.components.vacuum import (
    StateVacuumEntity,
    VacuumActivity,
    VacuumEntityFeature,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ALL_PROPS,
    BOX_TYPES,
    CLEANING_MODES,
    DOMAIN,
    FAN_SPEEDS,
    VACUUM_CARD_PROPS_REFERENCES,
)
from .coordinator import ViomiDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SERVICE_CLEAN_ZONE = "clean_zone"
SERVICE_CLEAN_AREA = "clean_area"
SERVICE_CLEAN_POINT = "clean_point"
SERVICE_CLEAN_SEGMENT = "clean_segment"
SERVICE_OBS_CLEAN_ZONE = "xiaomi_clean_zone"
SERVICE_OBS_CLEAN_POINT = "xiaomi_clean_point"
ATTR_ZONE_ARRAY = "zone"
ATTR_ZONE_REPEATER = "repeats"
ATTR_AREA_ARRAY = "area"
ATTR_AREA_REPEATER = "repeats"
ATTR_POINT = "point"
ATTR_SEGMENTS = "segments"

VACUUM_SERVICE_SCHEMA = vol.Schema({vol.Optional(ATTR_ENTITY_ID): cv.comp_entity_ids})
SERVICE_SCHEMA_CLEAN_ZONE = VACUUM_SERVICE_SCHEMA.extend(
    {
        vol.Required(ATTR_ZONE_ARRAY): vol.All(
            list,
            [
                vol.ExactSequence(
                    [vol.Coerce(float), vol.Coerce(float), vol.Coerce(float), vol.Coerce(float)]
                )
            ],
        ),
        vol.Required(ATTR_ZONE_REPEATER): vol.All(
            vol.Coerce(int), vol.Clamp(min=1, max=3)
        ),
    }
)
SERVICE_SCHEMA_CLEAN_AREA = VACUUM_SERVICE_SCHEMA.extend(
    {
        vol.Required(ATTR_AREA_ARRAY): vol.All(
            list,
            [
                vol.ExactSequence(
                    [vol.Coerce(float), vol.Coerce(float), vol.Coerce(float), vol.Coerce(float), vol.Coerce(float), vol.Coerce(float), vol.Coerce(float), vol.Coerce(float)]
                )
            ],
        ),
        vol.Required(ATTR_AREA_REPEATER): vol.All(
            vol.Coerce(int), vol.Clamp(min=1, max=3)
        ),
    }
)
SERVICE_SCHEMA_CLEAN_POINT = VACUUM_SERVICE_SCHEMA.extend(
    {
        vol.Required(ATTR_POINT): vol.All(
            vol.ExactSequence(
                [vol.Coerce(float), vol.Coerce(float)]
            )
        )
    }
)
SERVICE_SCHEMA_CLEAN_SEGMENT = VACUUM_SERVICE_SCHEMA.extend(
    {
        vol.Required(ATTR_SEGMENTS): vol.Any(
            vol.Coerce(int),
            [vol.Coerce(int)]
        ),
    }
)

SERVICE_TO_METHOD = {
    SERVICE_CLEAN_ZONE: {
        "method": "async_clean_zone",
        "schema": SERVICE_SCHEMA_CLEAN_ZONE,
    },
    SERVICE_CLEAN_AREA: {
        "method": "async_clean_area",
        "schema": SERVICE_SCHEMA_CLEAN_AREA,
    },
    SERVICE_CLEAN_POINT: {
        "method": "async_clean_point",
        "schema": SERVICE_SCHEMA_CLEAN_POINT,
    },
    SERVICE_CLEAN_SEGMENT: {
        "method": "async_clean_segment",
        "schema": SERVICE_SCHEMA_CLEAN_SEGMENT,
    },
    SERVICE_OBS_CLEAN_ZONE: {
        "method": "async_clean_zone",
        "schema": SERVICE_SCHEMA_CLEAN_ZONE,
    },
    SERVICE_OBS_CLEAN_POINT: {
        "method": "async_clean_point",
        "schema": SERVICE_SCHEMA_CLEAN_POINT,
    }
}

SUPPORT_VIOMI = (
    VacuumEntityFeature.STATE
    | VacuumEntityFeature.PAUSE
    | VacuumEntityFeature.STOP
    | VacuumEntityFeature.RETURN_HOME
    | VacuumEntityFeature.FAN_SPEED
    | VacuumEntityFeature.LOCATE
    | VacuumEntityFeature.SEND_COMMAND
    | VacuumEntityFeature.START
)

STATE_CODE_TO_STATE = {
    0: VacuumActivity.IDLE,
    1: VacuumActivity.IDLE,
    2: VacuumActivity.PAUSED,
    3: VacuumActivity.CLEANING,
    4: VacuumActivity.RETURNING,
    5: VacuumActivity.DOCKED,
    6: VacuumActivity.CLEANING,  # Vacuum & Mop
    7: VacuumActivity.CLEANING,  # Mop only
}

async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    """Set up the Viomi Vacuum V8 vacuum entity."""
    coordinator = entry.runtime_data

    device = ViomiVacuumEntity(coordinator.name, coordinator)

    coordinator.vacuum_entity = device

    async_add_entities([device], update_before_add=False)

class ViomiVacuumEntity(
    CoordinatorEntity[ViomiDataUpdateCoordinator],
    StateVacuumEntity,
):
    """Representation of the Viomi Vacuum V8 robot."""

    def __init__(
        self,
        name: str,
        coordinator: ViomiDataUpdateCoordinator,
    ) -> None:
        """Initialize the device handler."""
        super().__init__(coordinator)

        self._name = name
        self._vacuum = coordinator.vacuum
        self._last_clean_point = None

        self._attr_unique_id = f"{coordinator.mac_address}_vacuum"

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def vacuum_state(self):
        """Return the latest vacuum state."""
        return self.coordinator.data
    
    @property
    def device_info(self) -> DeviceInfo:
        """Return information about the device."""
        return self.coordinator.device_info

    @property
    def activity(self) -> VacuumActivity | None:
        """Return the current vacuum activity."""
        if self.vacuum_state is not None:
            try:
                return STATE_CODE_TO_STATE[int(self.vacuum_state["run_state"])]
            except KeyError:
                _LOGGER.error(
                    "State not supported, state_code: %s",
                    self.vacuum_state["run_state"],
                )
        return None

    @property
    def fan_speed(self):
        """Return the fan speed of the device."""
        if self.vacuum_state is not None:
            speed = self.vacuum_state['suction_grade']
            if speed in FAN_SPEEDS.values():
                return [
                    key for key,
                    value in FAN_SPEEDS.items() if value == speed][0]
            return speed

    @property
    def fan_speed_list(self):
        """Get the list of available fan speed steps of the device."""
        return list(sorted(FAN_SPEEDS.keys(), key=lambda s: FAN_SPEEDS[s]))

    @property
    def extra_state_attributes(self):
        """Return the specific state attributes of this device."""
        attrs = {}
        if self.vacuum_state is not None:
            attrs.update(self.vacuum_state)
            try:
                attrs['status'] = STATE_CODE_TO_STATE[int(
                    self.vacuum_state['run_state'])]
            except KeyError:
                return "Definition missing for state %s" % self.vacuum_state['run_state']
        return attrs

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success

    @property
    def supported_features(self):
        """Flag vacuum cleaner robot features that are supported."""
        return SUPPORT_VIOMI

    async def _try_command(self, mask_error, func, *args, **kwargs):
        """Call a vacuum command handling error messages."""
        try:
            await self.hass.async_add_executor_job(partial(func, *args, **kwargs))
            return True
        except DeviceException as exc:
            _LOGGER.error(mask_error, exc)
            return False

    async def async_start(self):
        """Start or resume the cleaning task."""
        mode = self.vacuum_state['mode']
        is_mop = self.vacuum_state['is_mop']
        actionMode = 0

        if mode == 4 and self._last_clean_point is not None:
            method = 'set_pointclean'
            param = [1, self._last_clean_point[0], self._last_clean_point[1]]
        else:
            if mode == 2:
                actionMode = 2
            else:
                if is_mop == 2:
                    actionMode = 3
                else:
                    actionMode = is_mop
            if mode == 3:
                method = 'set_mode'
                param = [3, 1]
            else:
                method = 'set_mode_withroom'
                param = [actionMode, 1, 0]
        await self._try_command("Unable to start the vacuum: %s", self._vacuum.raw_command, method, param)

    async def async_pause(self):
        """Pause the cleaning task."""
        mode = self.vacuum_state['mode']
        is_mop = self.vacuum_state['is_mop']
        actionMode = 0

        if mode == 4 and self._last_clean_point is not None:
            method = 'set_pointclean'
            param = [3, self._last_clean_point[0], self._last_clean_point[1]]
        else:
            if mode == 2:
                actionMode = 2
            else:
                if is_mop == 2:
                    actionMode = 3
                else:
                    actionMode = is_mop
            if mode == 3:
                method = 'set_mode'
                param = [3, 3]
            else:
                method = 'set_mode_withroom'
                param = [actionMode, 3, 0]
        await self._try_command("Unable to set pause: %s", self._vacuum.raw_command, method, param)

    async def async_stop(self, **kwargs):
        """Stop the vacuum cleaner."""
        mode = self.vacuum_state['mode']
        if mode == 3:
            method = 'set_mode'
            param = [3, 0]
        elif mode == 4:
            method = 'set_pointclean'
            param = [0, 0, 0]
            self._last_clean_point = None
        else:
            method = 'set_mode'
            param = [0]
        await self._try_command("Unable to stop: %s", self._vacuum.raw_command, method, param)

    async def async_set_fan_speed(self, fan_speed, **kwargs):
        """Set fan speed."""
        if fan_speed.capitalize() in FAN_SPEEDS:
            fan_speed = FAN_SPEEDS[fan_speed.capitalize()]
        else:
            try:
                fan_speed = int(fan_speed)
            except ValueError as exc:
                _LOGGER.error(
                    "Fan speed step not recognized (%s). "
                    "Valid speeds are: %s", exc, self.fan_speed_list, )
                return
        await self._try_command(
            "Unable to set fan speed: %s", self._vacuum.raw_command, 'set_suction', [
                fan_speed]
        )

    async def async_return_to_base(self, **kwargs):
        """Set the vacuum cleaner to return to the dock."""
        await self._try_command("Unable to return home: %s", self._vacuum.raw_command, 'set_charge', [1])

    async def async_locate(self, **kwargs):
        """Locate the vacuum cleaner."""
        await self._try_command("Unable to locate: %s", self._vacuum.raw_command, 'set_resetpos', [1])

    async def async_send_command(
        self,
        command: str,
        params: list[Any] | None = None,
    ) -> None:
        """Send a raw command to the vacuum."""
        before = await self.hass.async_add_executor_job(
            self.coordinator.vacuum.raw_command,
            "get_prop",
            ["run_state", "mode", "is_work", "is_mop", "box_type", "mop_type", "has_map", "has_newmap"],
        )

        _LOGGER.warning(
            "Viomi BEFORE %s(%s): %r",
            command,
            params or [],
            before,
        )

        result = await self.hass.async_add_executor_job(
            self.coordinator.vacuum.raw_command,
            command,
            params or [],
        )

        _LOGGER.warning(
            "Viomi COMMAND %s(%s) returned: %r",
            command,
            params or [],
            result,
        )

        await asyncio.sleep(3)

        after = await self.hass.async_add_executor_job(
            self.coordinator.vacuum.raw_command,
            "get_prop",
            ["run_state", "mode", "is_work", "is_mop", "box_type", "mop_type", "has_map", "has_newmap"],
        )

        _LOGGER.warning(
            "Viomi AFTER %s(%s): %r",
            command,
            params or [],
            after,
        )

    async def async_clean_zone(self, zone, repeats=1):
        """Clean selected zone for the number of repeats indicated."""
        result = []
        i = 0
        for z in zone:
            x1, y2, x2, y1 = z
            res = '_'.join(str(x)
                           for x in [i, 0, x1, y1, x1, y2, x2, y2, x2, y1])
            for _ in range(repeats):
                result.append(res)
                i += 1
        result = [i] + result

        await self._try_command("Unable to clean zone: %s", self._vacuum.raw_command, 'set_uploadmap', [1]) \
            and await self._try_command("Unable to clean zone: %s", self._vacuum.raw_command, 'set_zone', result) \
            and await self._try_command("Unable to clean zone: %s", self._vacuum.raw_command, 'set_mode', [3, 1])

    async def async_clean_area(self, area, repeats=1):
        """Clean selected area for the number of repeats indicated."""
        result = []
        i = 0
        for a in area:
            x1, y1, x2, y2, x3, y3, x4, y4 = a
            res = '_'.join(str(x)
                           for x in [i, 0, x1, y1, x2, y2, x3, y3, x4, y4])
            for _ in range(repeats):
                result.append(res)
                i += 1
        result = [i] + result

        await self._try_command("Unable to clean area: %s", self._vacuum.raw_command, 'set_uploadmap', [1]) \
            and await self._try_command("Unable to clean area: %s", self._vacuum.raw_command, 'set_zone', result) \
            and await self._try_command("Unable to clean area: %s", self._vacuum.raw_command, 'set_mode', [3, 1])

    async def async_clean_point(self, point):
        """Clean selected area"""
        x, y = point
        self._last_clean_point = point
        await self._try_command("Unable to clean point: %s", self._vacuum.raw_command, 'set_uploadmap', [0]) \
            and await self._try_command("Unable to clean point: %s", self._vacuum.raw_command, 'set_pointclean', [1, x, y])

    async def async_clean_segment(self, segments):
        """Clean selected segment(s) (rooms)"""
        if isinstance(segments, int):
            segments = [segments]

        await self._try_command("Unable to clean segments: %s", self._vacuum.raw_command, 'set_uploadmap', [1]) \
            and await self._try_command("Unable to clean segments: %s", self._vacuum.raw_command, 'set_mode_withroom', [0, 1, len(segments)] + segments)
