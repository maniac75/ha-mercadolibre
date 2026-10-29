"""Render the distributable card with Home Assistant's real template engine."""

from pathlib import Path

import yaml
from homeassistant.core import HomeAssistant
from homeassistant.helpers.template import Template

ENTITY = "sensor.mercado_libre_envios_en_seguimiento"
CARD = Path(__file__).resolve().parents[1] / "docs/mercadolibre-card.yaml"


def shipment(index, status="shipped", *, product=None, events=2):
    return {
        "shipment_id": f"example-{index}",
        "status": status,
        "substatus": None,
        "tracking_number": f"demo-{index}",
        "products": [{"name": product or f"Producto de ejemplo {index}", "quantity": 2}],
        "history": [
            {"status": status, "substatus": None, "date": f"2026-10-{i + 1:02d}T12:00:00Z"} for i in range(events)
        ],
    }


async def render(tmp_path, state, shipments=None, **extra):
    hass = HomeAssistant(str(tmp_path))
    await hass.config.async_set_time_zone("America/Santiago")
    attrs = (
        {}
        if shipments is None
        else {
            "shipments": shipments,
            "orders_checked": len(shipments),
            "orders_total": len(shipments),
            "unknown_shipments": 0,
            "truncated": False,
            "orders_without_shipment": 0,
        }
    )
    attrs.update(extra)
    hass.states.async_set(ENTITY, state, attrs)
    card = yaml.safe_load(CARD.read_text())
    return Template(card["content"], hass).async_render()


def test_hacs_example_matches_documented_card():
    example = CARD.parents[1] / "custom_components/mercadolibre_tracking/examples/mercadolibre-card.yaml"
    assert example.read_text() == CARD.read_text()
    card = yaml.safe_load(CARD.read_text())
    assert card["type"] == "markdown"


async def test_unavailable_does_not_present_stale_delivery_as_current(tmp_path):
    text = await render(tmp_path, "unavailable", [shipment(1, "delivered")])
    assert "Conexión no disponible" in text
    assert "Producto de ejemplo" not in text


async def test_empty_waiting_and_verified_zero_are_distinct(tmp_path):
    waiting = await render(tmp_path, "unknown")
    assert "Esperando datos" in waiting
    assert "0 envíos activos" not in waiting
    empty = await render(tmp_path, "0", [])
    assert "0 envíos activos" in empty
    assert "No hay envíos activos" in empty


async def test_partial_scan_does_not_claim_exact_active_count(tmp_path):
    text = await render(
        tmp_path,
        "unknown",
        [shipment(1, "future_state")],
        truncated=True,
        orders_checked=200,
        orders_total=250,
        unknown_shipments=1,
    )
    assert "Seguimiento parcial" in text
    assert "200 de 250" in text
    assert "pendiente de clasificación" in text
    assert "1 envío activo" not in text


async def test_full_history_and_all_available_shipments_remain_accessible(tmp_path):
    rows = [shipment(i, events=9) for i in range(10)]
    rows += [shipment(i, "delivered") for i in range(10, 16)]
    rows += [shipment(16, "cancelled"), shipment(17, "not_delivered")]
    text = await render(tmp_path, "10", rows)
    assert "Producto de ejemplo 9" in text
    assert "Producto de ejemplo 15" in text
    assert "Entregados · 6" in text
    assert "Cancelados o no entregados · 2" in text
    assert "09/10/2026 09:00" in text
    assert "example-17" in text
    assert "demo-9" in text


async def test_external_text_and_missing_dates_are_safe(tmp_path):
    row = shipment(1, product="<script>alert(1)</script> [click](javascript:alert(2))")
    row["history"] = [{"status": "shipped", "date": None, "substatus": "printed"}]
    row["tracking_number"] = None
    row["substatus"] = "first_visit"
    text = await render(tmp_path, "1", [row])
    assert "<script>" not in text
    assert "[click]" not in text
    assert "&lt;script&gt;" in text
    assert "Fecha no informada" in text
    assert "Etiqueta impresa" in text
    assert "Visita registrada" in text
    assert "Seguimiento aún no informado" in text
