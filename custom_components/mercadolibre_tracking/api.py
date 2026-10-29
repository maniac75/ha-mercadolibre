"""Read-only client; tokens are supplied by Home Assistant."""

import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiohttp import ClientError, ClientSession

from .const import ACTIVE_STATUSES, API_URL, MAX_ORDERS, PAGE_SIZE, TERMINAL_STATUSES


class ApiError(Exception):
    """Sanitized service error."""


class AuthError(ApiError):
    """Authentication or authorization refused."""


class MercadoLibreApi:
    """Only GET requests are exposed by this client."""

    def __init__(self, session: ClientSession, token: Callable[[], Awaitable[str]]):
        self.session = session
        self.token = token
        self._history_cache = {}

    async def get(self, path: str, params: dict | None = None) -> Any:
        if not path.startswith("/") or path.startswith("//") or "?" in path:
            raise ValueError("Invalid API resource")
        access_token = await self.token()
        try:
            async with asyncio.timeout(30):
                async with self.session.get(
                    API_URL + path,
                    params=params,
                    headers={"Authorization": f"Bearer {access_token}", "x-format-new": "true"},
                    allow_redirects=False,
                ) as response:
                    if response.status in (401, 403):
                        raise AuthError("Mercado Libre refused access")
                    if response.status == 429:
                        raise ApiError("Mercado Libre rate limit; next scheduled update will retry")
                    if response.status != 200:
                        raise ApiError(f"Mercado Libre HTTP {response.status}")
                    return await response.json()
        except (ClientError, TimeoutError, ValueError) as err:
            raise ApiError("Mercado Libre connection or response error") from err

    async def account(self) -> dict:
        user = await self.get("/users/me")
        if not isinstance(user, dict) or not isinstance(user.get("id"), int):
            raise ApiError("Invalid account response")
        return {"id": user["id"]}

    async def snapshot(self, buyer_id: int) -> dict:
        orders = []
        total = None
        for offset in range(0, MAX_ORDERS, PAGE_SIZE):
            page = await self.get(
                "/orders/search", {"buyer": buyer_id, "limit": PAGE_SIZE, "offset": offset, "sort": "date_desc"}
            )
            if not isinstance(page, dict) or not isinstance(page.get("results"), list):
                raise ApiError("Invalid orders response")
            paging = page.get("paging")
            if not isinstance(paging, dict):
                raise ApiError("Invalid orders pagination")
            reported_total = paging.get("total")
            if not isinstance(reported_total, int) or reported_total < 0:
                raise ApiError("Invalid orders count")
            total = reported_total
            batch = page["results"]
            if not batch and offset < total:
                raise ApiError("Incomplete orders pagination")
            orders.extend(batch)
            if offset + len(batch) >= total:
                break
        shipments = {}
        without_shipping = 0
        for order in orders:
            if not isinstance(order, dict) or not isinstance(order.get("id"), int):
                raise ApiError("Invalid order")
            if not isinstance(order.get("buyer"), dict) or "id" not in order["buyer"]:
                order = await self.get(f"/orders/{order['id']}")
            if not isinstance(order, dict) or not isinstance(order.get("buyer"), dict):
                raise ApiError("Invalid order detail")
            if order["buyer"].get("id") != buyer_id:
                raise AuthError("Order does not belong to the authorized account")
            shipping = order.get("shipping")
            if shipping is not None and not isinstance(shipping, dict):
                raise ApiError("Invalid shipping reference")
            sid = (shipping or {}).get("id")
            if sid is None:
                without_shipping += 1
                continue
            if not isinstance(sid, int):
                raise ApiError("Invalid shipment identifier")
            items = order.get("order_items", [])
            if not isinstance(items, list) or any(
                not isinstance(item, dict) or not isinstance(item.get("item"), dict) for item in items
            ):
                raise ApiError("Invalid order products")
            products = [
                {"name": item.get("item", {}).get("title"), "quantity": item.get("quantity")}
                for item in items
                if isinstance(item, dict)
            ]
            if sid in shipments:
                shipments[sid]["products"].extend(products)
                continue
            shipment = await self.get(f"/shipments/{sid}")
            if not isinstance(shipment, dict) or not isinstance(shipment.get("status"), str):
                raise ApiError("Invalid shipment response")
            state = shipment["status"]
            # Keep the final timeline visible after delivery. Cache completed
            # histories for six hours; always refresh active/unknown states.
            fingerprint = (state, shipment.get("substatus"))
            cached = self._history_cache.get(sid)
            history = cached[2] if cached else []
            if (
                state not in TERMINAL_STATUSES
                or not cached
                or cached[0] != fingerprint
                or time.monotonic() - cached[1] >= 21600
            ):
                raw_history = await self.get(f"/shipments/{sid}/history")
                if not isinstance(raw_history, list):
                    raise ApiError("Invalid shipment history")
                history = [
                    {key: event.get(key) for key in ("status", "substatus", "date")}
                    for event in raw_history
                    if isinstance(event, dict)
                ]
                self._history_cache[sid] = (fingerprint, time.monotonic(), history)
            shipments[sid] = {
                "shipment_id": str(sid),
                "status": state,
                "substatus": shipment.get("substatus"),
                "tracking_number": shipment.get("tracking_number"),
                "products": products,
                "history": history,
            }
        self._history_cache = {sid: cached for sid, cached in self._history_cache.items() if sid in shipments}
        values = list(shipments.values())
        return {
            "orders_total": total,
            "orders_checked": len(orders),
            "truncated": total is not None and len(orders) < total,
            "orders_without_shipment": without_shipping,
            "shipments": values,
            "active_count": sum(s["status"] in ACTIVE_STATUSES for s in values),
            "unknown_count": sum(s["status"] not in ACTIVE_STATUSES | TERMINAL_STATUSES for s in values),
        }
