"""OAuth setup and reauthentication."""

import logging
from collections.abc import Mapping
from typing import Any

from homeassistant.config_entries import SOURCE_REAUTH
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ApiError, AuthError, MercadoLibreApi
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class OAuth2FlowHandler(config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN):
    DOMAIN = DOMAIN
    VERSION = 1

    @property
    def logger(self):
        return _LOGGER

    async def async_oauth_create_entry(self, data: dict[str, Any]):
        async def token():
            return data["token"]["access_token"]

        api = MercadoLibreApi(async_get_clientsession(self.hass), token)
        try:
            account = await api.account()
            # Validate the actual buyer resource before accepting setup.
            await api.get("/orders/search", {"buyer": account["id"], "limit": 1})
        except AuthError:
            return self.async_abort(reason="access_denied")
        except ApiError:
            return self.async_abort(reason="cannot_connect")
        await self.async_set_unique_id(str(account["id"]))
        if self.source == SOURCE_REAUTH:
            self._abort_if_unique_id_mismatch()
            return self.async_update_reload_and_abort(self._get_reauth_entry(), data_updates=data)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="Mercado Libre Compras", data=data)

    async def async_step_reauth(self, entry_data: Mapping[str, Any]):
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        if user_input is None:
            return self.async_show_form(step_id="reauth_confirm")
        return await self.async_step_user()
