"""One serialized cloud poll every 30 minutes."""

import logging
from datetime import timedelta

from aiohttp import ClientResponseError
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ApiError, AuthError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class MercadoLibreCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry, api):
        super().__init__(hass, _LOGGER, name=DOMAIN, config_entry=entry, update_interval=timedelta(minutes=30))
        self.api = api
        self.buyer_id = int(entry.unique_id)

    async def _async_update_data(self):
        try:
            return await self.api.snapshot(self.buyer_id)
        except AuthError as err:
            raise ConfigEntryAuthFailed("Mercado Libre authorization refused") from err
        except ClientResponseError as err:
            if err.status in (400, 401, 403):
                raise ConfigEntryAuthFailed("Mercado Libre OAuth authorization expired") from err
            raise UpdateFailed("Mercado Libre OAuth temporarily unavailable") from err
        except ApiError as err:
            raise UpdateFailed(str(err)) from err
