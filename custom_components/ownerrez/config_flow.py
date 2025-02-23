"""Config flow for OwnerRez integration."""
from __future__ import annotations

import logging
from typing import Any

from ownerrez_wrapper import API
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ownerrez"

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("username"): str,
        vol.Required("token"): str,
        vol.Required("property_id"): str,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    client = API(
        username=data["username"],
        token=data["token"]
    )
    
    try:
        # Attempt to fetch property to validate credentials
        await hass.async_add_executor_job(
            client.getproperty, int(data["property_id"])
        )
    except Exception as err:
        raise InvalidAuth from err

    return {"title": f"OwnerRez Property {data['property_id']}"}

@config_entries.HANDLERS.register(DOMAIN)
class OwnerRezConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OwnerRez."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth.""" 