"""Config flow for the Viomi Vacuum V8 integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from miio import DeviceException, ViomiVacuum  # pylint: disable=import-error
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN

from .const import DEFAULT_NAME, DOMAIN


class ViomiVacuumConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a Viomi Vacuum V8 config flow."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle the user setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            token = user_input[CONF_TOKEN].strip()
            name = user_input.get(CONF_NAME, "").strip() or DEFAULT_NAME

            try:
                vacuum = ViomiVacuum(host, token)
                info = await self.hass.async_add_executor_job(vacuum.info)
            except (DeviceException, OSError):
                errors["base"] = "cannot_connect"
            else:
                if not info.mac_address:
                    errors["base"] = "cannot_connect"
                else:
                    await self.async_set_unique_id(info.mac_address.lower())
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=name,
                        data={
                            CONF_HOST: host,
                            CONF_TOKEN: token,
                            CONF_NAME: name,
                        },
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_TOKEN): vol.All(
                        str,
                        vol.Length(min=32, max=32),
                    ),
                    vol.Optional(
                        CONF_NAME,
                        default=DEFAULT_NAME,
                    ): str,
                }
            ),
            errors=errors,
        )