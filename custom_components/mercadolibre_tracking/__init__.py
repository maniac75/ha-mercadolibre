"""Mercado Libre purchases integration."""

from homeassistant.const import Platform
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.config_entry_oauth2_flow import OAuth2Session, async_get_config_entry_implementation

from .api import MercadoLibreApi
from .const import DOMAIN
from .coordinator import MercadoLibreCoordinator

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass, entry):
    implementation = await async_get_config_entry_implementation(hass, entry)
    oauth = OAuth2Session(hass, entry, implementation)

    async def token():
        # Home Assistant serializes refreshes and persists the ROTATED refresh
        # token in the existing config entry before any API request proceeds.
        await oauth.async_ensure_token_valid()
        return oauth.token["access_token"]

    coordinator = MercadoLibreCoordinator(hass, entry, MercadoLibreApi(async_get_clientsession(hass), token))
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
