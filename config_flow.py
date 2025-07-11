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
            except ValueError:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_USERNAME, default="admin"): str,
            vol.Required(CONF_PASSWORD): cv.string,
        })

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    async def _test_connection(self, host: str, username: str, password: str):
        """Test if we can connect to the device."""
        session = async_get_clientsession(self.hass)
        
        # Format password as 3 digits (PA parameter format)
        password_formatted = password.zfill(3)[-3:]
        
        # Test authentication
        url = f"http://{host}/log.cgi"
        params = {
            'user': username,
            'pass': password_formatted
        }
        
        try:
            async with session.get(url, params=params, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                
                if 'ID' not in data:
                    raise ValueError("Authentication failed - no ID received")
                
                auth_id = data['ID']
                
                # Test data retrieval with the auth ID
                data_url = f"http://{host}/ajax_data.cgi"
                data_params = {'pgd': auth_id}
                
                async with session.get(data_url, params=data_params, timeout=10) as data_response:
                    data_response.raise_for_status()
                    await data_response.json()
                    
        except aiohttp.ClientError as err:
            _LOGGER.error("Connection test failed: %s", err)
            raise
        except Exception as err:
            _LOGGER.error("Authentication test failed: %s", err)
            raise ValueError(f"Authentication failed: {err}")