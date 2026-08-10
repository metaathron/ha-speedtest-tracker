"""Config flow for Speedtest Tracker."""
from __future__ import annotations

import secrets
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components import webhook
from homeassistant.core import callback
from homeassistant.helpers.selector import BooleanSelector, NumberSelector, NumberSelectorConfig, TextSelector
from homeassistant.helpers.update_coordinator import UpdateFailed

from .api import (
    SpeedtestTrackerApiClient,
    SpeedtestTrackerApiClientAuthenticationError,
    SpeedtestTrackerApiClientCommunicationError,
    SpeedtestTrackerApiClientForbiddenError,
    SpeedtestTrackerApiClientInvalidResponseError,
    SpeedtestTrackerApiClientSSLError,
)
from .const import (
    CONF_BASE_URL,
    CONF_BEARER_TOKEN,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    CONF_VERIFY_SSL,
    CONF_WEBHOOK_ID,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEOUT,
    DOMAIN,
)


def _generate_webhook_id() -> str:
    """Generate a random, hard-to-guess webhook id.

    The webhook id acts as an unauthenticated bearer token for the webhook
    URL, so it needs to be long and unpredictable.
    """
    return secrets.token_hex(32)


async def _validate_input(hass, data: dict[str, Any]) -> dict[str, Any]:
    from homeassistant.helpers.aiohttp_client import async_get_clientsession

    client = SpeedtestTrackerApiClient(
        async_get_clientsession(hass),
        data[CONF_BASE_URL],
        data[CONF_BEARER_TOKEN],
        int(data[CONF_TIMEOUT]),
        bool(data[CONF_VERIFY_SSL]),
    )
    latest = await client.get_latest_result()
    stats = await client.get_stats()
    if latest.get("message") != "ok" or stats.get("message") != "ok":
        raise SpeedtestTrackerApiClientInvalidResponseError("API response did not return message=ok")
    return {"title": "Speedtest Tracker"}


class SpeedtestTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Speedtest Tracker."""

    VERSION = 1

    def __init__(self) -> None:
        super().__init__()
        self._webhook_id_default: str | None = None

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if self._webhook_id_default is None:
            self._webhook_id_default = _generate_webhook_id()

        if user_input is not None:
            try:
                info = await _validate_input(self.hass, user_input)
            except SpeedtestTrackerApiClientAuthenticationError:
                errors["base"] = "invalid_auth"
            except SpeedtestTrackerApiClientForbiddenError:
                errors["base"] = "forbidden"
            except SpeedtestTrackerApiClientSSLError:
                errors["base"] = "ssl_error"
            except SpeedtestTrackerApiClientCommunicationError:
                errors["base"] = "cannot_connect"
            except SpeedtestTrackerApiClientInvalidResponseError:
                errors["base"] = "invalid_response"
            except Exception:
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input[CONF_BASE_URL].rstrip("/"))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=info["title"],
                    data={
                        CONF_BASE_URL: user_input[CONF_BASE_URL].rstrip("/"),
                        CONF_BEARER_TOKEN: user_input[CONF_BEARER_TOKEN],
                        CONF_TIMEOUT: int(user_input[CONF_TIMEOUT]),
                        CONF_VERIFY_SSL: bool(user_input[CONF_VERIFY_SSL]),
                        CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL]),
                        CONF_WEBHOOK_ID: user_input[CONF_WEBHOOK_ID].strip(),
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL): TextSelector(),
                vol.Required(CONF_BEARER_TOKEN): TextSelector(),
                vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): NumberSelector(
                    NumberSelectorConfig(min=10, max=86400, mode="box")
                ),
                vol.Required(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): NumberSelector(
                    NumberSelectorConfig(min=5, max=300, mode="box")
                ),
                vol.Required(CONF_VERIFY_SSL, default=True): BooleanSelector(),
                vol.Required(CONF_WEBHOOK_ID, default=self._webhook_id_default): TextSelector(),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()

        # Entries created before webhook_id became user-configurable already have
        # one (it has always been auto-generated on setup), so this only kicks in
        # as a last-resort fallback.
        if self._webhook_id_default is None:
            self._webhook_id_default = entry.data.get(CONF_WEBHOOK_ID) or _generate_webhook_id()

        if user_input is not None:
            merged = {
                **entry.data,
                CONF_BASE_URL: user_input[CONF_BASE_URL].rstrip("/"),
                CONF_BEARER_TOKEN: user_input[CONF_BEARER_TOKEN],
                CONF_TIMEOUT: int(user_input[CONF_TIMEOUT]),
                CONF_VERIFY_SSL: bool(user_input[CONF_VERIFY_SSL]),
                CONF_WEBHOOK_ID: user_input[CONF_WEBHOOK_ID].strip(),
            }
            try:
                await _validate_input(self.hass, merged)
            except SpeedtestTrackerApiClientAuthenticationError:
                errors["base"] = "invalid_auth"
            except SpeedtestTrackerApiClientForbiddenError:
                errors["base"] = "forbidden"
            except SpeedtestTrackerApiClientSSLError:
                errors["base"] = "ssl_error"
            except SpeedtestTrackerApiClientCommunicationError:
                errors["base"] = "cannot_connect"
            except SpeedtestTrackerApiClientInvalidResponseError:
                errors["base"] = "invalid_response"
            except Exception:
                errors["base"] = "unknown"
            else:
                old_webhook_id = entry.data.get(CONF_WEBHOOK_ID)
                if old_webhook_id and old_webhook_id != merged[CONF_WEBHOOK_ID]:
                    webhook.async_unregister(self.hass, old_webhook_id)
                self.hass.config_entries.async_update_entry(
                    entry,
                    data={
                        **entry.data,
                        CONF_BASE_URL: merged[CONF_BASE_URL],
                        CONF_BEARER_TOKEN: merged[CONF_BEARER_TOKEN],
                        CONF_TIMEOUT: merged[CONF_TIMEOUT],
                        CONF_VERIFY_SSL: merged[CONF_VERIFY_SSL],
                        CONF_WEBHOOK_ID: merged[CONF_WEBHOOK_ID],
                    },
                )
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reconfigure_successful")

        schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL, default=entry.data[CONF_BASE_URL]): TextSelector(),
                vol.Required(CONF_BEARER_TOKEN, default=entry.data[CONF_BEARER_TOKEN]): TextSelector(),
                vol.Required(
                    CONF_TIMEOUT,
                    default=entry.options.get(CONF_TIMEOUT, entry.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)),
                ): NumberSelector(NumberSelectorConfig(min=5, max=300, mode="box")),
                vol.Required(
                    CONF_VERIFY_SSL,
                    default=entry.options.get(CONF_VERIFY_SSL, entry.data.get(CONF_VERIFY_SSL, True)),
                ): BooleanSelector(),
                vol.Required(CONF_WEBHOOK_ID, default=self._webhook_id_default): TextSelector(),
            }
        )
        return self.async_show_form(step_id="reconfigure", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SpeedtestTrackerOptionsFlow()


class SpeedtestTrackerOptionsFlow(config_entries.OptionsFlowWithReload):
    """Handle options for Speedtest Tracker."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL]),
                    CONF_TIMEOUT: int(user_input[CONF_TIMEOUT]),
                    CONF_VERIFY_SSL: bool(user_input[CONF_VERIFY_SSL]),
                },
            )

        entry = self.config_entry
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=entry.options.get(
                        CONF_SCAN_INTERVAL,
                        entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                    ),
                ): NumberSelector(NumberSelectorConfig(min=10, max=86400, mode="box")),
                vol.Required(
                    CONF_TIMEOUT,
                    default=entry.options.get(CONF_TIMEOUT, entry.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)),
                ): NumberSelector(NumberSelectorConfig(min=5, max=300, mode="box")),
                vol.Required(
                    CONF_VERIFY_SSL,
                    default=entry.options.get(CONF_VERIFY_SSL, entry.data.get(CONF_VERIFY_SSL, True)),
                ): BooleanSelector(),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
