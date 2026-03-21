"""Speedtest Tracker integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components import webhook
from homeassistant.helpers.network import get_url

from .const import CONF_WEBHOOK_ID, DOMAIN, PLATFORMS
from .coordinator import SpeedtestTrackerCoordinator

SIGNAL_WEBHOOK_REFRESH = f"{DOMAIN}_webhook_refresh"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Speedtest Tracker from a config entry."""
    coordinator = SpeedtestTrackerCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"coordinator": coordinator}

    webhook_id = entry.data[CONF_WEBHOOK_ID]

    async def _handle_webhook(hass: HomeAssistant, webhook_id: str, request):
        await coordinator.async_request_refresh()
        async_dispatcher_send(hass, SIGNAL_WEBHOOK_REFRESH, entry.entry_id)
        return None

    webhook.async_register(
        hass,
        DOMAIN,
        f"{DOMAIN}_{entry.title}",
        webhook_id,
        _handle_webhook,
        allowed_methods=("POST", "GET"),
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    webhook_id = entry.data[CONF_WEBHOOK_ID]
    webhook.async_unregister(hass, webhook_id)

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
