"""Summary sensor with sanitized shipment data."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([MercadoLibreSummary(entry.runtime_data, entry.unique_id)])


class MercadoLibreSummary(CoordinatorEntity, SensorEntity):
    _attr_name = "Mercado Libre Envíos en seguimiento"
    _attr_icon = "mdi:package-variant"
    # Keep products, tracking and timelines live without persisting them in Recorder.
    _unrecorded_attributes = frozenset({"shipments"})

    def __init__(self, coordinator, account_id):
        super().__init__(coordinator)
        self._attr_unique_id = f"{account_id}_shipments_summary"

    @property
    def native_value(self):
        # A bounded scan must not pretend to be a complete account-wide count.
        if self.coordinator.data["truncated"] or self.coordinator.data["unknown_count"]:
            return None
        return self.coordinator.data["active_count"]

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        return {
            "orders_total": data["orders_total"],
            "orders_checked": data["orders_checked"],
            "truncated": data["truncated"],
            "unknown_shipments": data["unknown_count"],
            "orders_without_shipment": data["orders_without_shipment"],
            "shipments": data["shipments"],
        }
