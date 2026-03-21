"""Data coordinator for Speedtest Tracker."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    SpeedtestTrackerApiClient,
    SpeedtestTrackerApiClientAuthenticationError,
    SpeedtestTrackerApiClientCommunicationError,
    SpeedtestTrackerApiClientInvalidResponseError,
)
from .const import (
    CONF_BASE_URL,
    CONF_BEARER_TOKEN,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    CONF_VERIFY_SSL,
    RUNNING_RETRY_SECONDS,
)

_LOGGER = logging.getLogger(__name__)


class SpeedtestTrackerCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate Speedtest Tracker data updates."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        options = entry.options
        self.api = SpeedtestTrackerApiClient(
            async_get_clientsession(hass),
            entry.data[CONF_BASE_URL],
            entry.data[CONF_BEARER_TOKEN],
            int(options.get(CONF_TIMEOUT, entry.data.get(CONF_TIMEOUT))),
            bool(options.get(CONF_VERIFY_SSL, entry.data.get(CONF_VERIFY_SSL))),
        )
        update_interval = timedelta(
            seconds=int(options.get(CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL)))
        )
        self._retry_unsub = None
        self._post_run_unsub = None
        super().__init__(
            hass,
            _LOGGER,
            name="Speedtest Tracker",
            update_interval=update_interval,
        )

    def _schedule_refresh_in(self, seconds: int) -> None:
        def _retry(_: Any) -> None:
            if self._retry_unsub is not None and seconds == RUNNING_RETRY_SECONDS:
                self._retry_unsub = None
            if self._post_run_unsub is not None and seconds != RUNNING_RETRY_SECONDS:
                self._post_run_unsub = None
            self.hass.async_create_task(self.async_request_refresh())

        return async_call_later(self.hass, seconds, _retry)

    def _schedule_running_retry(self) -> None:
        if self._retry_unsub is None:
            self._retry_unsub = self._schedule_refresh_in(RUNNING_RETRY_SECONDS)

    def schedule_post_run_refresh(self) -> None:
        if self._post_run_unsub is not None:
            self._post_run_unsub()
        self._post_run_unsub = self._schedule_refresh_in(RUNNING_RETRY_SECONDS)

    def _merge_keep_previous_when_running(
        self,
        latest_payload: dict[str, Any],
        stats_payload: dict[str, Any],
    ) -> dict[str, Any]:
        latest_data = latest_payload.get("data", {})
        status = latest_data.get("status")

        if status == "running" and self.data:
            self._schedule_running_retry()
            new_data = dict(self.data)
            new_data["meta"] = {
                **new_data.get("meta", {}),
                "currently_running": True,
                "last_running_status": status,
            }
            return new_data

        return {
            "latest": latest_data,
            "stats": stats_payload.get("data", {}),
            "meta": {"currently_running": False},
        }

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            latest_payload = await self.api.get_latest_result()
            stats_payload = await self.api.get_stats()
            return self._merge_keep_previous_when_running(latest_payload, stats_payload)
        except SpeedtestTrackerApiClientAuthenticationError as err:
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except (
            SpeedtestTrackerApiClientCommunicationError,
            SpeedtestTrackerApiClientInvalidResponseError,
        ) as err:
            raise UpdateFailed(str(err)) from err
