"""Traeger Cook Guide — Home Assistant Integration."""
from __future__ import annotations

import asyncio
import logging

import homeassistant.helpers.config_validation as cv
from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, WWW_SUBDIR, HTML_FILENAME
from .helpers import async_create_helpers, async_remove_helpers
from .automations import async_create_automations, async_remove_automations
from .www_install import install_www_files, remove_www_files

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

_DASHBOARD_YAML = (
    "type: iframe\n"
    f"url: /local/{WWW_SUBDIR}/{HTML_FILENAME}\n"
    'aspect_ratio: "100%"\n'
    "title: Traeger Cook Guide"
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Traeger Cook Guide from a config entry."""

    # 1. Copy HTML to /config/www/traeger_cook_guide/ (file I/O in executor)
    await hass.async_add_executor_job(install_www_files, hass)

    # 2. Wait for HA to fully start, then create helpers + automations
    async def _do_setup(_event=None) -> None:
        # Poll until input_select, input_number, input_boolean, automation
        # storage collections are all available
        for attempt in range(30):
            sel = hass.data.get("input_select")
            num = hass.data.get("input_number")
            bol = hass.data.get("input_boolean")
            aut = hass.data.get("automation")

            sel_ready = sel is not None and hasattr(sel, "storage_collection")
            num_ready = num is not None and hasattr(num, "storage_collection")
            bol_ready = bol is not None and hasattr(bol, "storage_collection")
            aut_ready = aut is not None and hasattr(
                getattr(aut, "storage_collection", None), "async_create_item"
            )

            if sel_ready and num_ready and bol_ready and aut_ready:
                _LOGGER.debug(
                    "Traeger Cook Guide: all components ready after %d attempts",
                    attempt,
                )
                break

            _LOGGER.debug(
                "Traeger Cook Guide: waiting for components "
                "(attempt %d/30, sel=%s num=%s bol=%s aut=%s)",
                attempt + 1, sel_ready, num_ready, bol_ready, aut_ready,
            )
            await asyncio.sleep(3)
        else:
            _LOGGER.error(
                "Traeger Cook Guide: timed out waiting for HA components. "
                "Helpers and automations were NOT created. "
                "Please restart HA and try again."
            )
            return

        await async_create_helpers(hass)
        await async_create_automations(hass)
        _notify_dashboard(hass)
        _LOGGER.info("Traeger Cook Guide: setup complete — helpers and automations created")

    if hass.is_running:
        # HA already fully running (user added integration manually after boot)
        hass.async_create_task(_do_setup())
    else:
        # HA still booting — wait for homeassistant_started event
        @callback
        def _on_started(_event=None) -> None:
            hass.async_create_task(_do_setup())

        hass.bus.async_listen_once("homeassistant_started", _on_started)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle integration unload."""
    _LOGGER.info("Traeger Cook Guide: unloaded")
    return True


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Clean up on full removal."""
    await async_remove_helpers(hass)
    await async_remove_automations(hass)
    await hass.async_add_executor_job(remove_www_files, hass)
    _LOGGER.info("Traeger Cook Guide: fully removed")


def _notify_dashboard(hass: HomeAssistant) -> None:
    """Show persistent notification with dashboard card YAML."""
    try:
        persistent_notification.async_create(
            hass,
            title="Traeger Cook Guide — Last Step",
            message=(
                "Setup complete! Helpers and automations created automatically.\n\n"
                "**Add the dashboard card:**\n\n"
                "1. Dashboard -> Edit -> Add Card -> Manual\n"
                "2. Paste this YAML:\n\n"
                f"```yaml\n{_DASHBOARD_YAML}\n```\n\n"
                "Then open the guide and paste your HA Long-Lived Access Token "
                "on first load (Profile -> Long-Lived Access Tokens -> Create Token)."
            ),
            notification_id="traeger_cook_guide_setup",
        )
    except Exception as err:
        _LOGGER.warning("Traeger Cook Guide: notification error: %s", err)
