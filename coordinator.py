"""DataUpdateCoordinator for NECTOR200."""
import logging
from datetime import timedelta, datetime
from typing import Any, Dict, Optional
import aiohttp
import asyncio
import json

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class NECTOR200Coordinator(DataUpdateCoordinator):
    """Class to manage fetching NECTOR200 data."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        """Initialize."""
        self.ip = entry.data[CONF_HOST]
        self.username = entry.data[CONF_USERNAME]
        self.password = entry.data[CONF_PASSWORD]
        self.session = aiohttp.ClientSession()
        self._auth_id: Optional[str] = None
        self._last_keepalive = None
        self._keepalive_task = None
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from NECTOR200."""
        try:
            # Ensure we're authenticated
            if not self._auth_id:
                await self._authenticate()
            
            # Get current status
            url = f"http://{self.ip}/ajax_data.cgi"
            params = {'pgd': self._auth_id}
            
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 401 or response.status == 403:
                    # Try to re-authenticate
                    self._auth_id = None
                    await self._authenticate()
                    # Retry the request
                    params = {'pgd': self._auth_id}
                    async with self.session.get(url, params=params, timeout=10) as retry_response:
                        retry_response.raise_for_status()
                        data = await retry_response.json()
                else:
                    response.raise_for_status()
                    data = await response.json()
                
            # Convert string values to appropriate types
            return {
                "temperature": float(data.get("temp", 0)),
                "setpoint": float(data.get("sttmp", 0)),
                "standby": data.get("stby", "0") == "1",
                "light": data.get("ligh", "0") == "1",
                "defrost": data.get("def", "0") == "1",
                "alarm": data.get("almst", "0") == "1",
                "recording": data.get("recst", "0") == "1",
            }
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}")

    async def _authenticate(self) -> None:
        """Authenticate with the NECTOR200 device."""
        try:
            # Format password as 3 digits
            password_formatted = self.password.zfill(3)[-3:]
            
            _LOGGER.info("Attempting authentication with user='%s', formatted password='%s'", 
                        self.username, password_formatted)
            
            url = f"http://{self.ip}/log.cgi"
            params = {
                'user': self.username,
                'pass': password_formatted
            }
            
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 401:
                    # Check if it's a "too many users" error
                    text = await response.text()
                    if "Too many users" in text:
                        _LOGGER.error("Authentication failed: Too many users connected to NECTOR200. "
                                     "Close other connections or power cycle the device.")
                        raise ConfigEntryAuthFailed(
                            "Too many users connected to NECTOR200. "
                            "Please close other connections or power cycle the device."
                        )
                    else:
                        _LOGGER.error("Authentication failed with 401. Check PA parameter on device. "
                                     "Current password: '%s' (formatted as '%s')", 
                                     self.password, password_formatted)
                        raise ConfigEntryAuthFailed(
                            f"Authentication failed: Invalid password. "
                            f"Check PA parameter on NECTOR200 device (tried: {password_formatted})"
                        )
                response.raise_for_status()
                data = await response.json()
                
            if 'ID' not in data:
                raise ConfigEntryAuthFailed("Authentication failed - no ID received")
                
            self._auth_id = str(data['ID'])
            _LOGGER.info("Successfully authenticated with NECTOR200, received ID: %s", self._auth_id)
            
            # Start keepalive task
            if self._keepalive_task:
                self._keepalive_task.cancel()
            self._keepalive_task = self.hass.async_create_task(self._keepalive_loop())
            
        except aiohttp.ClientError as err:
            _LOGGER.error("Authentication request failed: %s", err)
            raise ConfigEntryAuthFailed(f"Authentication failed: {err}")

    async def _keepalive_loop(self) -> None:
        """Send keepalive messages every 90 seconds."""
        while True:
            try:
                await asyncio.sleep(90)  # Send every 90 seconds (well under the 2-minute limit)
                await self._send_keepalive()
            except Exception as err:
                _LOGGER.error("Keepalive failed: %s", err)

    async def _send_keepalive(self) -> None:
        """Send keepalive message to maintain session."""
        if not self._auth_id:
            return
            
        try:
            url = f"http://{self.ip}/alive.cgi"
            params = {'pgd': self._auth_id}
            
            async with self.session.get(url, params=params, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                _LOGGER.debug("Keepalive response: %s", data)
                
        except Exception as err:
            _LOGGER.error("Failed to send keepalive: %s", err)
            # If keepalive fails, clear auth ID to force re-authentication
            self._auth_id = None

    async def async_toggle_button(self, button_idx: int) -> bool:
        """Toggle a button function (standby, light, or defrost)."""
        try:
            if not self._auth_id:
                await self._authenticate()
                
            url = f"http://{self.ip}/btnfunct.cgi"
            params = {
                'btnIdx': str(button_idx),
                'pgd': self._auth_id
            }
            
            async with self.session.get(url, params=params, timeout=10) as response:
                response.raise_for_status()
                # Response contains the updated status
                return response.status == 200
                
        except Exception as err:
            _LOGGER.error("Failed to toggle button %s: %s", button_idx, err)
            return False

    async def async_set_standby(self, enable: bool) -> bool:
        """Set standby mode."""
        # Check current state
        current_standby = self.data.get("standby", False)
        # Only toggle if needed
        if current_standby != enable:
            return await self.async_toggle_button(0)
        return True

    async def async_toggle_light(self) -> bool:
        """Toggle light."""
        return await self.async_toggle_button(1)

    async def async_toggle_defrost(self) -> bool:
        """Toggle defrost."""
        return await self.async_toggle_button(2)

    async def async_set_temperature(self, temperature: float) -> bool:
        """Set target temperature (setpoint)."""
        try:
            if not self._auth_id:
                await self._authenticate()
            
            # First, we need to get the current setpoint to calculate the difference
            current_setpoint = self.data.get("setpoint", 0)
            difference = temperature - current_setpoint
            
            if abs(difference) < 0.1:  # Already at target
                return True
            
            # The API uses incremental changes
            # We need to find the setpoint parameter indices
            # Based on the manual, setpoint is at level 0, line 0
            url = f"http://{self.ip}/pdatamod.cgi"
            params = {
                'iParDatIdx': '0',  # Level 0 (Setpoint level)
                'idline': '0',      # Line 0 (first parameter)
                'optype': 'mod',    # Modify operation
                'val': str(difference),  # Increment/decrement value
                'pgd': self._auth_id
            }
            
            async with self.session.get(url, params=params, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                _LOGGER.debug("Set temperature response: %s", data)
                return True
                
        except Exception as err:
            _LOGGER.error("Failed to set temperature: %s", err)
            return False

    async def async_close(self):
        """Close the session and cancel tasks."""
        if self._keepalive_task:
            self._keepalive_task.cancel()
        await self.session.close()

    async def async_set_parameter(self, param: str, value: str) -> bool:
        """Legacy method for compatibility - redirects to appropriate methods."""
        # Map old parameter names to new methods
        if param == "stby":
            return await self.async_set_standby(value == "1")
        elif param == "ligh":
            return await self.async_toggle_light()
        elif param == "def":
            return await self.async_toggle_defrost()
        elif param == "Set":
            try:
                return await self.async_set_temperature(float(value))
            except ValueError:
                return False
        return False