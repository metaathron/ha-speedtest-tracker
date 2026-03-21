"""Binary sensor platform for Speedtest Tracker."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import SpeedtestTrackerCoordinatorEntity


def _dig(data: dict[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


@dataclass(frozen=True, kw_only=True)
class SpeedtestTrackerBinarySensorDescription(BinarySensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], bool | None]
    object_id: str


DESCRIPTIONS = (
    SpeedtestTrackerBinarySensorDescription(
        key="healthy",
        name="Healthy",
        object_id="speedtest_tracker_healthy",
        icon="mdi:heart-pulse",
        value_fn=lambda data: _dig(data, "latest", "healthy"),
    ),
    SpeedtestTrackerBinarySensorDescription(
        key="scheduled",
        name="Scheduled",
        object_id="speedtest_tracker_scheduled",
        icon="mdi:calendar-clock",
        value_fn=lambda data: _dig(data, "latest", "scheduled"),
    ),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([SpeedtestTrackerBinarySensor(coordinator, entry, d) for d in DESCRIPTIONS])


class SpeedtestTrackerBinarySensor(SpeedtestTrackerCoordinatorEntity, BinarySensorEntity):
    """Representation of a Speedtest Tracker binary sensor."""

    entity_description: SpeedtestTrackerBinarySensorDescription

    def __init__(self, coordinator, entry: ConfigEntry, description: SpeedtestTrackerBinarySensorDescription) -> None:
        super().__init__(coordinator, entry)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_has_entity_name = True
        self._attr_name = description.name
        self._attr_suggested_object_id = description.object_id

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.value_fn(self.coordinator.data)
