"""DataUpdateCoordinator for NECTOR200."""
import logging
from datetime import timedelta
from typing import Any, Dict
import aiohttp
import asyncio

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryAuthFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class NECTOR200Coordinator(DataUpdateCoordinator):
    """Class to manage fetching NECTOR200 data."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        """Initialize."""
        self.ip = entry.data["host"]
        self.username = entry.data["username"]
        self.password = entry.data["password"]
        self.session = aiohttp.ClientSession()
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from NECTOR200."""
        try:
            # Get current status
            url = f"http://{self.ip}/ajax_data.cgi?pgd='{self.password}'"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 401:
                    raise ConfigEntryAuthFailed("Invalid authentication")
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

    async def async_set_parameter(self, param: str, value: str) -> bool:
        """Set a parameter on the NECTOR200."""
        try:
            url = f"http://{self.ip}/set_param.cgi"
            data = {
                'pgd': self.password,
                'param': param,
                'value': value
            }
            async with self.session.post(url, data=data, timeout=10) as response:
                response.raise_for_status()
                return response.status == 200
        except Exception as err:
            _LOGGER.error("Failed to set parameter %s: %s", param, err)
            return False

    async def async_close(self):
        """Close the session."""
        await self.session.close()