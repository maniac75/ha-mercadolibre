import asyncio
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from homeassistant.helpers.config_entry_oauth2_flow import OAuth2Session

from custom_components.mercadolibre_tracking.application_credentials import async_get_auth_implementation


async def test_pkce_uses_registered_chilean_endpoints():
    credential = SimpleNamespace(client_id="test-client", client_secret="test-secret")
    impl = await async_get_auth_implementation(SimpleNamespace(), "mercadolibre_tracking", credential)
    assert impl.extra_authorize_data["code_challenge_method"] == "S256"
    assert len(impl.extra_token_resolve_data["code_verifier"]) >= 43
    assert impl.authorize_url == "https://auth.mercadolibre.cl/authorization"
    assert impl.token_url == "https://api.mercadolibre.com/oauth/token"
    assert impl.client_secret == "test-secret"


async def test_native_refresh_serializes_and_saves_rotated_token():
    entry = SimpleNamespace(
        data={"token": {"access_token": "expired", "refresh_token": "old-refresh", "expires_at": 0}}
    )
    rotated = {"access_token": "new", "refresh_token": "new-refresh", "expires_at": time.time() + 3600}
    implementation = SimpleNamespace(async_refresh_token=AsyncMock(return_value=rotated))

    def update(config_entry, *, data):
        config_entry.data = data

    update_entry = Mock(side_effect=update)
    hass = SimpleNamespace(config_entries=SimpleNamespace(async_update_entry=update_entry))
    session = OAuth2Session(hass, entry, implementation)
    await asyncio.gather(*[session.async_ensure_token_valid() for _ in range(5)])
    implementation.async_refresh_token.assert_awaited_once()
    update_entry.assert_called_once()
    assert entry.data["token"]["refresh_token"] == "new-refresh"
    assert session.valid_token
