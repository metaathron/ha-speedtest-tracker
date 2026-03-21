"""Button platform for Speedtest Tracker."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SpeedtestTrackerCoordinatorEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([SpeedtestTrackerRunButton(coordinator, entry)])


class SpeedtestTrackerRunButton(SpeedtestTrackerCoordinatorEntity, ButtonEntity):
    """Button to start a speedtest run."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_run_test"
        self._attr_has_entity_name = True
        self._attr_name = "Run test"
        self._attr_icon = "mdi:speedometer"
        self._attr_suggested_object_id = "speedtest_tracker_run_test"

    async def async_press(self) -> None:
        await self.coordinator.api.run_speedtest()
        self.coordinator.schedule_post_run_refresh()
        await self.coordinator.async_request_refresh()
