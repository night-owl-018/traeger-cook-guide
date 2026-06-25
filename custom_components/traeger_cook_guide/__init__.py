"""
Traeger Cook Guide — Home Assistant Integration.

On install (async_setup_entry):
  1. Copies traeger_cook_guide.html -> /config/www/traeger_cook_guide/
  2. Creates all 6 helpers  (input_select x2, input_number x2, input_boolean x2)
  3. Creates all 9 automations
  4. Shows a persistent_notification with the dashboard card YAML to paste

On uninstall:
  - Removes helpers, automations, and www files
"""
from __future__ import annotations

import asyncio
import logging

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_call_later

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

    # 1. Copy HTML file — runs in executor (file I/O)
    await hass.async_add_executor_job(install_www_files, hass)

    # 2. Helpers + automations need input_* and automation components
    #    to be fully loaded. We wait for HA to finish starting, then run.
    async def _do_setup(_now=None) -> None:
        # Extra safety: wait until input_select is actually in hass.data
        for attempt in range(20):
            if (
                "input_select" in hass.data
                and "input_number" in hass.data
                and "input_boolean" in hass.data
                and "automation" in hass.data
            ):
                break
            _LOGGER.debug(
                "Traeger Cook Guide: waiting for components (attempt %d/20)...",
                attempt + 1,
            )
            await asyncio.sleep(2)

        await async_create_helpers(hass)
        await async_create_automations(hass)
        _notify_dashboard(hass)
        _LOGGER.info("Traeger Cook Guide: all helpers and automations created")

    if hass.is_running:
        # HA already running — components are ready, go immediately
        hass.async_create_task(_do_setup())
    else:
        # HA still starting — wait until fully started then run
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
        hass.components.persistent_notification.async_create(
            title="Traeger Cook Guide — Last Step",
            message=(
                "Setup complete! Helpers and automations created automatically.\n\n"
                "Add the dashboard card:\n\n"
                "1. Dashboard -> Edit -> Add Card -> Manual\n"
                "2. Paste this YAML:\n\n"
                f"```yaml\n{_DASHBOARD_YAML}\n```\n\n"
                "Then open the guide and enter your HA Long-Lived Access Token "
                "on first load (Profile -> Long-Lived Access Tokens -> Create Token)."
            ),
            notification_id="traeger_cook_guide_setup",
        )
    except Exception as err:
        _LOGGER.warning("Traeger Cook Guide: could not create notification: %s", err)
