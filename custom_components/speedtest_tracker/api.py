"""API client for Speedtest Tracker."""
from __future__ import annotations

from typing import Any

import aiohttp

from .const import LATEST_PATH, RUN_PATH, STATS_PATH


class SpeedtestTrackerApiClientError(Exception):
    """Base API client error."""


class SpeedtestTrackerApiClientCommunicationError(SpeedtestTrackerApiClientError):
    """Communication error."""


class SpeedtestTrackerApiClientAuthenticationError(SpeedtestTrackerApiClientError):
    """Authentication error."""


class SpeedtestTrackerApiClientInvalidResponseError(SpeedtestTrackerApiClientError):
    """Invalid response error."""


class SpeedtestTrackerApiClient:
    """Speedtest Tracker API client."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        base_url: str,
        bearer_token: str,
        timeout: int,
        verify_ssl: bool,
    ) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")
        self._bearer_token = bearer_token
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._verify_ssl = verify_ssl

    @property
    def base_url(self) -> str:
        return self._base_url

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self._bearer_token}",
        }

    async def _request(self, method: str, path: str) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        try:
            async with self._session.request(
                method,
                url,
                headers=self._headers(),
                timeout=self._timeout,
                ssl=self._verify_ssl,
            ) as response:
                if response.status in (401, 403):
                    raise SpeedtestTrackerApiClientAuthenticationError(
                        f"Authentication failed with status {response.status}"
                    )
                if response.status >= 400:
                    text = await response.text()
                    raise SpeedtestTrackerApiClientCommunicationError(
                        f"HTTP {response.status}: {text[:200]}"
                    )
                payload = await response.json(content_type=None)
        except SpeedtestTrackerApiClientError:
            raise
        except (aiohttp.ClientError, TimeoutError) as err:
            raise SpeedtestTrackerApiClientCommunicationError(str(err)) from err

        if not isinstance(payload, dict) or "data" not in payload:
            raise SpeedtestTrackerApiClientInvalidResponseError(
                "Response payload does not contain 'data'"
            )
        return payload

    async def get_latest_result(self) -> dict[str, Any]:
        return await self._request("GET", LATEST_PATH)

    async def get_stats(self) -> dict[str, Any]:
        return await self._request("GET", STATS_PATH)

    async def run_speedtest(self) -> dict[str, Any]:
        return await self._request("POST", RUN_PATH)
