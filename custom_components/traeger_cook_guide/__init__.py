"""
Traeger Cook Guide — Home Assistant Integration.

On install (async_setup_entry):
  1. Copies traeger_cook_guide.html → /config/www/traeger_cook_guide/
  2. Creates all 6 helpers  (input_select × 2, input_number × 2, input_boolean × 2)
  3. Creates all 9 automations
  4. Shows a persistent_notification with the single dashboard card YAML to paste

On uninstall (async_unload_entry / async_remove_entry):
  - Removes helpers, automations, and www files
"""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_call_later

from .const import DOMAIN, WWW_SUBDIR, HTML_FILENAME
from .helpers import async_create_helpers, async_remove_helpers
from .automations import async_create_automations, async_remove_automations
from .www_install import install_www_files, remove_www_files

_LOGGER = logging.getLogger(__name__)

_DASHBOARD_YAML = (
    "type: iframe\n"
    f"url: /local/{WWW_SUBDIR}/{HTML_FILENAME}\n"
    'aspect_ratio: "100%"\n'
    "title: Traeger Cook Guide"
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Full zero-touch setup — called once when the integration is first added."""

    # 1. Install HTML to /config/www/
    await hass.async_add_executor_job(install_www_files, hass)

    # 2. Create helpers — schedule slightly after startup so input_* components are ready
    async def _delayed_setup(_now=None):
        await async_create_helpers(hass)
        await async_create_automations(hass)
        _notify_dashboard(hass)

    # If HA is already running (e.g. user-initiated re-add) call immediately,
    # otherwise defer 3 s so all built-in components are initialised
    if hass.is_running:
        await _delayed_setup()
    else:
        async_call_later(hass, 3, _delayed_setup)

    _LOGGER.info("Traeger Cook Guide: setup complete")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Called when user removes the integration from the UI."""
    _LOGGER.info("Traeger Cook Guide: unloading")
    return True


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Called after unload — clean up helpers, automations, and www files."""
    await async_remove_helpers(hass)
    await async_remove_automations(hass)
    await hass.async_add_executor_job(remove_www_files, hass)
    _LOGGER.info("Traeger Cook Guide: fully removed")


def _notify_dashboard(hass: HomeAssistant) -> None:
    """Fire a one-time persistent notification with the dashboard card YAML."""
    hass.components.persistent_notification.async_create(
        title="🔥 Traeger Cook Guide — Last Step",
        message=(
            "Everything is set up automatically!\n\n"
            "**One final step — add the dashboard card:**\n\n"
            "1. Go to your dashboard → ✏️ Edit\n"
            "2. **Add Card** → **Manual**\n"
            "3. Paste this YAML:\n\n"
            f"```yaml\n{_DASHBOARD_YAML}\n```\n\n"
            "That's it. The cook guide is live. "
            "Open it and enter your HA Long-Lived Access Token on first load "
            "(Profile → Long-Lived Access Tokens → Create Token)."
        ),
        notification_id="traeger_cook_guide_setup",
    )
