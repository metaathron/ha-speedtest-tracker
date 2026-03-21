"""Entity helpers for Speedtest Tracker."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class SpeedtestTrackerCoordinatorEntity(CoordinatorEntity):
    """Base coordinator entity."""

    def __init__(self, coordinator, entry, stats_device: bool = False) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._stats_device = stats_device

    @property
    def device_info(self) -> DeviceInfo:
        if self._stats_device:
            return DeviceInfo(
                identifiers={(DOMAIN, f"{self._entry.entry_id}_stats")},
                name="Speedtest Tracker Statistics",
                manufacturer="Speedtest Tracker",
                model="API",
                configuration_url=self._entry.data.get("base_url"),
            )
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="Speedtest Tracker",
            manufacturer="Speedtest Tracker",
            model="API",
            configuration_url=self._entry.data.get("base_url"),
        )
