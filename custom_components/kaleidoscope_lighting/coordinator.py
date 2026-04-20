from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed
from datetime import timedelta
import logging

from .api import KaleidoscopeAPI

_LOGGER = logging.getLogger(__name__)


class KaleidoscopeCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, base_url, interval):
        super().__init__(
            hass,
            logger=_LOGGER,
            name="kaleidoscope_lighting",
            update_interval=timedelta(seconds=interval),
        )
        self.api = KaleidoscopeAPI(hass, base_url)

    async def _async_update_data(self):
        try:
            _LOGGER.debug("Fetching fixtures from %s", self.api.base_url)
            return await self.api.get_fixtures()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
