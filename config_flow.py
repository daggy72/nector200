"""Config flow for NECTOR200 integration."""
import logging
from typing import Any, Dict
import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NECTOR200."""

    VERSION = 1

    async def async_step_user(self, user_input: Dict[str, Any] = None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            try:
                await self._test_connection(
                    user_input[CONF_HOST],
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD]
                )
                
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=f"NECTOR200 ({user_input[CONF_HOST]})",
                    data=user_input
                )
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_USERNAME, default="admin"): str,
            vol.Required(CONF_PASSWORD): str,
        })

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    async def _test_connection(self, host: str, username: str, password: str):
        """Test if we can connect to the device."""
        session = async_get_clientsession(self.hass)
        url = f"http://{host}/ajax_data.cgi?pgd='{password}'"
        async with session.get(url, timeout=10) as response:
            response.raise_for_status()
            await response.json()