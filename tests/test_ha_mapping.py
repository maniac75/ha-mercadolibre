from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.mercadolibre_tracking.api import ApiError, AuthError
from custom_components.mercadolibre_tracking.coordinator import MercadoLibreCoordinator
from custom_components.mercadolibre_tracking.sensor import MercadoLibreSummary


@pytest.mark.parametrize("truncated,unknown,expected", [(False, 0, 3), (True, 0, None), (False, 1, None)])
def test_incomplete_scan_never_presents_exact_count(truncated, unknown, expected):
    summary = SimpleNamespace(
        coordinator=SimpleNamespace(data={"truncated": truncated, "unknown_count": unknown, "active_count": 3})
    )
    assert MercadoLibreSummary.native_value.fget(summary) == expected


async def test_permission_refusal_requires_reauthentication():
    coordinator = SimpleNamespace(api=SimpleNamespace(snapshot=AsyncMock(side_effect=AuthError("refused"))), buyer_id=7)
    with pytest.raises(ConfigEntryAuthFailed):
        await MercadoLibreCoordinator._async_update_data(coordinator)
    coordinator.api.snapshot.assert_awaited_once_with(7)


async def test_temporary_failure_marks_data_unavailable():
    coordinator = SimpleNamespace(
        api=SimpleNamespace(snapshot=AsyncMock(side_effect=ApiError("rate limit"))), buyer_id=7
    )
    with pytest.raises(UpdateFailed, match="rate limit"):
        await MercadoLibreCoordinator._async_update_data(coordinator)
