import re

import aiohttp
import pytest
from aioresponses import aioresponses

from custom_components.mercadolibre_tracking.api import ApiError, AuthError, MercadoLibreApi

BASE = "https://api.mercadolibre.com"


async def token():
    return "fixture-access-token"


def order(oid, sid, buyer=7):
    return {
        "id": oid,
        "buyer": {"id": buyer},
        "shipping": {"id": sid},
        "order_items": [{"item": {"title": "Producto"}, "quantity": 1}],
    }


@pytest.mark.asyncio
async def test_shared_shipment_redaction_and_active_history():
    with aioresponses() as mock:
        mock.get(
            re.compile(BASE + "/orders/search.*"),
            payload={"paging": {"total": 2}, "results": [order(1, 10), order(2, 10)]},
        )
        mock.get(
            BASE + "/shipments/10",
            payload={"status": "shipped", "tracking_number": "T1", "receiver_address": {"street_name": "PRIVATE"}},
        )
        mock.get(
            BASE + "/shipments/10/history",
            payload=[{"status": "shipped", "date": "2026-10-27T12:00:00Z", "private": "PRIVATE"}],
        )
        async with aiohttp.ClientSession() as session:
            data = await MercadoLibreApi(session, token).snapshot(7)
        assert data["active_count"] == 1
        assert len(data["shipments"]) == 1
        assert len(data["shipments"][0]["products"]) == 2
        assert data["shipments"][0]["history"][0]["status"] == "shipped"
        assert "PRIVATE" not in str(data)
        assert all(method == "GET" for method, _ in mock.requests)


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [401, 403])
async def test_refused_access_stops_before_shipments(status):
    with aioresponses() as mock:
        mock.get(re.compile(BASE + "/orders/search.*"), status=status)
        async with aiohttp.ClientSession() as session:
            with pytest.raises(AuthError):
                await MercadoLibreApi(session, token).snapshot(7)
        assert len(mock.requests) == 1


@pytest.mark.asyncio
async def test_foreign_order_is_rejected():
    with aioresponses() as mock:
        mock.get(
            re.compile(BASE + "/orders/search.*"), payload={"paging": {"total": 1}, "results": [order(1, 10, buyer=9)]}
        )
        async with aiohttp.ClientSession() as session:
            with pytest.raises(AuthError):
                await MercadoLibreApi(session, token).snapshot(7)
        assert len(mock.requests) == 1


@pytest.mark.asyncio
async def test_rate_limit_has_no_immediate_retry():
    with aioresponses() as mock:
        mock.get(BASE + "/users/me", status=429, payload={"access_token": "PRIVATE"})
        async with aiohttp.ClientSession() as session:
            with pytest.raises(ApiError, match="rate limit") as error:
                await MercadoLibreApi(session, token).account()
        assert "PRIVATE" not in str(error.value)
        assert len(mock.requests) == 1


@pytest.mark.asyncio
async def test_pagination_completes_without_duplicate_packages():
    first = [order(i, 10) for i in range(50)]
    with aioresponses() as mock:
        mock.get(re.compile(BASE + "/orders/search.*"), payload={"paging": {"total": 51}, "results": first})
        mock.get(re.compile(BASE + "/orders/search.*"), payload={"paging": {"total": 51}, "results": [order(50, 10)]})
        mock.get(BASE + "/shipments/10", payload={"status": "delivered"})
        mock.get(BASE + "/shipments/10/history", payload=[])
        async with aiohttp.ClientSession() as session:
            data = await MercadoLibreApi(session, token).snapshot(7)
        assert data["orders_checked"] == 51
        assert not data["truncated"]
        assert data["active_count"] == 0
        assert len(data["shipments"]) == 1
        assert len(mock.requests) == 4


@pytest.mark.asyncio
async def test_missing_page_is_not_reported_as_zero():
    with aioresponses() as mock:
        mock.get(re.compile(BASE + "/orders/search.*"), payload={"paging": {"total": 4}, "results": []})
        async with aiohttp.ClientSession() as session:
            with pytest.raises(ApiError, match="Incomplete"):
                await MercadoLibreApi(session, token).snapshot(7)


@pytest.mark.asyncio
async def test_unknown_state_does_not_become_delivered_or_active():
    with aioresponses() as mock:
        mock.get(re.compile(BASE + "/orders/search.*"), payload={"paging": {"total": 1}, "results": [order(1, 10)]})
        mock.get(BASE + "/shipments/10", payload={"status": "future_state"})
        mock.get(BASE + "/shipments/10/history", payload=[])
        async with aiohttp.ClientSession() as session:
            data = await MercadoLibreApi(session, token).snapshot(7)
        assert data["unknown_count"] == 1
        assert data["shipments"][0]["status"] == "future_state"


@pytest.mark.asyncio
async def test_scan_limit_is_explicit():
    with aioresponses() as mock:
        for offset in range(0, 200, 50):
            mock.get(
                re.compile(BASE + "/orders/search.*"),
                payload={"paging": {"total": 201}, "results": [order(i, None) for i in range(offset, offset + 50)]},
            )
        async with aiohttp.ClientSession() as session:
            data = await MercadoLibreApi(session, token).snapshot(7)
        assert data["truncated"]
        assert data["orders_checked"] == 200
        assert data["orders_without_shipment"] == 200


@pytest.mark.asyncio
async def test_delivery_keeps_final_history_and_reuses_completed_cache():
    with aioresponses() as mock:
        orders_url = re.compile(BASE + "/orders/search.*")
        for state in ("shipped", "delivered", "delivered"):
            mock.get(orders_url, payload={"paging": {"total": 1}, "results": [order(1, 10)]})
            mock.get(BASE + "/shipments/10", payload={"status": state})
        mock.get(BASE + "/shipments/10/history", payload=[{"status": "shipped", "date": "2026-10-27"}])
        mock.get(
            BASE + "/shipments/10/history",
            payload=[{"status": "shipped", "date": "2026-10-27"}, {"status": "delivered", "date": "2026-10-28"}],
        )
        async with aiohttp.ClientSession() as session:
            api = MercadoLibreApi(session, token)
            active = await api.snapshot(7)
            delivered = await api.snapshot(7)
            again = await api.snapshot(7)
        assert active["active_count"] == 1
        assert delivered["active_count"] == 0
        assert delivered["shipments"][0]["history"][-1]["status"] == "delivered"
        assert again["shipments"][0]["history"] == delivered["shipments"][0]["history"]
        history_calls = next(calls for (_, url), calls in mock.requests.items() if str(url).endswith("/history"))
        assert len(history_calls) == 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {"paging": None, "results": []},
        {"paging": {"total": 1}, "results": [{"id": 1, "buyer": {"id": 7}, "shipping": []}]},
        {
            "paging": {"total": 1},
            "results": [{"id": 1, "buyer": {"id": 7}, "shipping": {"id": 10}, "order_items": [{"item": None}]}],
        },
    ],
)
async def test_malformed_nested_data_is_a_controlled_error(payload):
    with aioresponses() as mock:
        mock.get(re.compile(BASE + "/orders/search.*"), payload=payload)
        async with aiohttp.ClientSession() as session:
            with pytest.raises(ApiError):
                await MercadoLibreApi(session, token).snapshot(7)


@pytest.mark.asyncio
async def test_connection_failure_is_sanitized():
    with aioresponses() as mock:
        mock.get(BASE + "/users/me", exception=aiohttp.ClientConnectionError("PRIVATE"))
        async with aiohttp.ClientSession() as session:
            with pytest.raises(ApiError) as error:
                await MercadoLibreApi(session, token).account()
        assert "PRIVATE" not in str(error.value)
