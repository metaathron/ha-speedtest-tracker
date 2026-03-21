"""Sensor platform for Speedtest Tracker."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfDataRate, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import ATTR_BYTES_PER_SECOND, ATTR_WEBHOOK_URL, DOMAIN
from .entity import SpeedtestTrackerCoordinatorEntity


def _dig(data: dict[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


@dataclass(frozen=True, kw_only=True)
class SpeedtestTrackerSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any]
    attr_fn: Callable[[dict[str, Any], ConfigEntry], dict[str, Any]] | None = None
    stats_device: bool = False
    object_id: str
    entity_category = None


CURRENT_SENSORS: tuple[SpeedtestTrackerSensorDescription, ...] = (
    SpeedtestTrackerSensorDescription(
        key="download",
        name="Download",
        object_id="speedtest_tracker_download",
        icon="mdi:download-network",
        native_unit_of_measurement=UnitOfDataRate.MEGABITS_PER_SECOND,
        value_fn=lambda data: round((_dig(data, "latest", "download_bits") or 0) / 1_000_000, 2)
        if _dig(data, "latest", "download_bits") is not None
        else None,
        attr_fn=lambda data, entry: {
            ATTR_BYTES_PER_SECOND: _dig(data, "latest", "download"),
        },
    ),
    SpeedtestTrackerSensorDescription(
        key="upload",
        name="Upload",
        object_id="speedtest_tracker_upload",
        icon="mdi:upload-network",
        native_unit_of_measurement=UnitOfDataRate.MEGABITS_PER_SECOND,
        value_fn=lambda data: round((_dig(data, "latest", "upload_bits") or 0) / 1_000_000, 2)
        if _dig(data, "latest", "upload_bits") is not None
        else None,
        attr_fn=lambda data, entry: {
            ATTR_BYTES_PER_SECOND: _dig(data, "latest", "upload"),
        },
    ),
    SpeedtestTrackerSensorDescription(
        key="ping",
        name="Ping",
        object_id="speedtest_tracker_ping",
        icon="mdi:timer-outline",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        value_fn=lambda data: _dig(data, "latest", "ping"),
    ),
    SpeedtestTrackerSensorDescription(
        key="packet_loss",
        name="Packet loss",
        object_id="speedtest_tracker_packet_loss",
        icon="mdi:percent-outline",
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda data: _dig(data, "latest", "data", "packetLoss"),
    ),
    SpeedtestTrackerSensorDescription(
        key="ping_jitter",
        name="Ping jitter",
        object_id="speedtest_tracker_ping_jitter",
        icon="mdi:waves-arrow-right",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        value_fn=lambda data: _dig(data, "latest", "data", "ping", "jitter"),
    ),
    SpeedtestTrackerSensorDescription(
        key="download_latency_low",
        name="Download latency low",
        object_id="speedtest_tracker_download_latency_low",
        icon="mdi:download",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        value_fn=lambda data: _dig(data, "latest", "data", "download", "latency", "low"),
    ),
    SpeedtestTrackerSensorDescription(
        key="download_latency_iqm",
        name="Download latency IQM",
        object_id="speedtest_tracker_download_latency_iqm",
        icon="mdi:download",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        value_fn=lambda data: _dig(data, "latest", "data", "download", "latency", "iqm"),
    ),
    SpeedtestTrackerSensorDescription(
        key="download_latency_high",
        name="Download latency high",
        object_id="speedtest_tracker_download_latency_high",
        icon="mdi:download",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        value_fn=lambda data: _dig(data, "latest", "data", "download", "latency", "high"),
    ),
    SpeedtestTrackerSensorDescription(
        key="download_jitter",
        name="Download jitter",
        object_id="speedtest_tracker_download_jitter",
        icon="mdi:download",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        value_fn=lambda data: _dig(data, "latest", "data", "download", "latency", "jitter"),
    ),
    SpeedtestTrackerSensorDescription(
        key="upload_latency_low",
        name="Upload latency low",
        object_id="speedtest_tracker_upload_latency_low",
        icon="mdi:upload",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        value_fn=lambda data: _dig(data, "latest", "data", "upload", "latency", "low"),
    ),
    SpeedtestTrackerSensorDescription(
        key="upload_latency_iqm",
        name="Upload latency IQM",
        object_id="speedtest_tracker_upload_latency_iqm",
        icon="mdi:upload",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        value_fn=lambda data: _dig(data, "latest", "data", "upload", "latency", "iqm"),
    ),
    SpeedtestTrackerSensorDescription(
        key="upload_latency_high",
        name="Upload latency high",
        object_id="speedtest_tracker_upload_latency_high",
        icon="mdi:upload",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        value_fn=lambda data: _dig(data, "latest", "data", "upload", "latency", "high"),
    ),
    SpeedtestTrackerSensorDescription(
        key="upload_jitter",
        name="Upload jitter",
        object_id="speedtest_tracker_upload_jitter",
        icon="mdi:upload",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        value_fn=lambda data: _dig(data, "latest", "data", "upload", "latency", "jitter"),
    ),
    SpeedtestTrackerSensorDescription(
        key="download_elapsed",
        name="Download elapsed",
        object_id="speedtest_tracker_download_elapsed",
        icon="mdi:clock-outline",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        value_fn=lambda data: _dig(data, "latest", "data", "download", "elapsed"),
    ),
    SpeedtestTrackerSensorDescription(
        key="upload_elapsed",
        name="Upload elapsed",
        object_id="speedtest_tracker_upload_elapsed",
        icon="mdi:clock-outline",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        value_fn=lambda data: _dig(data, "latest", "data", "upload", "elapsed"),
    ),
    SpeedtestTrackerSensorDescription(
        key="server",
        name="Server",
        object_id="speedtest_tracker_server",
        icon="mdi:server-network",
        value_fn=lambda data: _dig(data, "latest", "data", "server", "name"),
        attr_fn=lambda data, entry: {
            "server_id": _dig(data, "latest", "data", "server", "id"),
            "server_country": _dig(data, "latest", "data", "server", "country"),
            "server_location": _dig(data, "latest", "data", "server", "location"),
            "isp": _dig(data, "latest", "data", "isp"),
            "host": _dig(data, "latest", "data", "server", "host"),
            "port": _dig(data, "latest", "data", "server", "port"),
            "ip": _dig(data, "latest", "data", "server", "ip"),
        },
    ),
    SpeedtestTrackerSensorDescription(
        key="status",
        name="Status",
        object_id="speedtest_tracker_status",
        icon="mdi:list-status",
        value_fn=lambda data: _dig(data, "latest", "status"),
        attr_fn=lambda data, entry: {
            "service": _dig(data, "latest", "service"),
            "scheduled": _dig(data, "latest", "scheduled"),
            ATTR_WEBHOOK_URL: f"/api/webhook/{entry.data.get('webhook_id')}",
        },
    ),
    SpeedtestTrackerSensorDescription(
        key="last_test_time",
        name="Last test time",
        object_id="speedtest_tracker_last_test_time",
        icon="mdi:clock-time-eight-outline",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: _dig(data, "latest", "updated_at"),
    ),
    SpeedtestTrackerSensorDescription(
        key="result_url",
        name="Result URL",
        object_id="speedtest_tracker_result_url",
        icon="mdi:link-variant",
        value_fn=lambda data: _dig(data, "latest", "data", "result", "url"),
    ),
)

STAT_SENSORS: tuple[SpeedtestTrackerSensorDescription, ...] = (
    SpeedtestTrackerSensorDescription(
        key="ping_avg",
        name="Ping avg",
        object_id="speedtest_tracker_statistics_ping_avg",
        icon="mdi:timer-outline",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        value_fn=lambda data: _dig(data, "stats", "ping", "avg"),
        stats_device=True,
    ),
    SpeedtestTrackerSensorDescription(
        key="ping_min",
        name="Ping min",
        object_id="speedtest_tracker_statistics_ping_min",
        icon="mdi:timer-outline",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        value_fn=lambda data: _dig(data, "stats", "ping", "min"),
        stats_device=True,
    ),
    SpeedtestTrackerSensorDescription(
        key="ping_max",
        name="Ping max",
        object_id="speedtest_tracker_statistics_ping_max",
        icon="mdi:timer-outline",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        value_fn=lambda data: _dig(data, "stats", "ping", "max"),
        stats_device=True,
    ),
    SpeedtestTrackerSensorDescription(
        key="download_avg",
        name="Download avg",
        object_id="speedtest_tracker_statistics_download_avg",
        icon="mdi:download-network",
        native_unit_of_measurement=UnitOfDataRate.MEGABITS_PER_SECOND,
        value_fn=lambda data: round((_dig(data, "stats", "download", "avg_bits") or 0) / 1_000_000, 2)
        if _dig(data, "stats", "download", "avg_bits") is not None
        else None,
        stats_device=True,
    ),
    SpeedtestTrackerSensorDescription(
        key="download_min",
        name="Download min",
        object_id="speedtest_tracker_statistics_download_min",
        icon="mdi:download-network",
        native_unit_of_measurement=UnitOfDataRate.MEGABITS_PER_SECOND,
        value_fn=lambda data: round((_dig(data, "stats", "download", "min_bits") or 0) / 1_000_000, 2)
        if _dig(data, "stats", "download", "min_bits") is not None
        else None,
        stats_device=True,
    ),
    SpeedtestTrackerSensorDescription(
        key="download_max",
        name="Download max",
        object_id="speedtest_tracker_statistics_download_max",
        icon="mdi:download-network",
        native_unit_of_measurement=UnitOfDataRate.MEGABITS_PER_SECOND,
        value_fn=lambda data: round((_dig(data, "stats", "download", "max_bits") or 0) / 1_000_000, 2)
        if _dig(data, "stats", "download", "max_bits") is not None
        else None,
        stats_device=True,
    ),
    SpeedtestTrackerSensorDescription(
        key="upload_avg",
        name="Upload avg",
        object_id="speedtest_tracker_statistics_upload_avg",
        icon="mdi:upload-network",
        native_unit_of_measurement=UnitOfDataRate.MEGABITS_PER_SECOND,
        value_fn=lambda data: round((_dig(data, "stats", "upload", "avg_bits") or 0) / 1_000_000, 2)
        if _dig(data, "stats", "upload", "avg_bits") is not None
        else None,
        stats_device=True,
    ),
    SpeedtestTrackerSensorDescription(
        key="upload_min",
        name="Upload min",
        object_id="speedtest_tracker_statistics_upload_min",
        icon="mdi:upload-network",
        native_unit_of_measurement=UnitOfDataRate.MEGABITS_PER_SECOND,
        value_fn=lambda data: round((_dig(data, "stats", "upload", "min_bits") or 0) / 1_000_000, 2)
        if _dig(data, "stats", "upload", "min_bits") is not None
        else None,
        stats_device=True,
    ),
    SpeedtestTrackerSensorDescription(
        key="upload_max",
        name="Upload max",
        object_id="speedtest_tracker_statistics_upload_max",
        icon="mdi:upload-network",
        native_unit_of_measurement=UnitOfDataRate.MEGABITS_PER_SECOND,
        value_fn=lambda data: round((_dig(data, "stats", "upload", "max_bits") or 0) / 1_000_000, 2)
        if _dig(data, "stats", "upload", "max_bits") is not None
        else None,
        stats_device=True,
    ),
    SpeedtestTrackerSensorDescription(
        key="total_results",
        name="Total results",
        object_id="speedtest_tracker_statistics_total_results",
        icon="mdi:counter",
        value_fn=lambda data: _dig(data, "stats", "total_results"),
        stats_device=True,
    ),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    entities: list[SensorEntity] = [
        SpeedtestTrackerSensor(coordinator, entry, description)
        for description in (*CURRENT_SENSORS, *STAT_SENSORS)
    ]
    async_add_entities(entities)


class SpeedtestTrackerSensor(SpeedtestTrackerCoordinatorEntity, SensorEntity):
    """Representation of a Speedtest Tracker sensor."""

    entity_description: SpeedtestTrackerSensorDescription

    def __init__(self, coordinator, entry: ConfigEntry, description: SpeedtestTrackerSensorDescription) -> None:
        super().__init__(coordinator, entry, description.stats_device)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_has_entity_name = True
        self._attr_name = description.name
        self._attr_suggested_object_id = description.object_id

    @property
    def native_value(self):
        if self.entity_description.key == "last_test_time":
            value = self.entity_description.value_fn(self.coordinator.data)
            if not value:
                return None
            try:
                naive_dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None
            tz = dt_util.get_time_zone(self.hass.config.time_zone)
            if tz is None:
                tz = dt_util.DEFAULT_TIME_ZONE
            return naive_dt.replace(tzinfo=tz)
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self):
        if self.entity_description.key == "status":
            attrs = self.entity_description.attr_fn(self.coordinator.data, self._entry) or {}
            attrs["webhook_id"] = self._entry.data.get("webhook_id")
            return attrs
        if self.entity_description.attr_fn is None:
            return None
        attrs = self.entity_description.attr_fn(self.coordinator.data, self._entry)
        return {k: v for k, v in attrs.items() if v is not None}
