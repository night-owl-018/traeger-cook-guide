"""
Create and remove the 6 HA helpers that power the Traeger Cook Guide.

Uses the same internal StorageCollection API that the HA UI uses, so helpers
appear in Settings → Helpers, are editable in the UI, and survive restarts —
exactly as if the user created them by hand.
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.components.input_select import InputSelect
from homeassistant.components.input_number import InputNumber
from homeassistant.components.input_boolean import InputBoolean

from .const import (
    DOMAIN,
    HELPER_P1_MEAT_TYPE,
    HELPER_P2_MEAT_TYPE,
    HELPER_P1_TARGET_TEMP,
    HELPER_P2_TARGET_TEMP,
    HELPER_P1_ALERT_SENT,
    HELPER_P2_ALERT_SENT,
    MEAT_OPTIONS,
)

_LOGGER = logging.getLogger(__name__)


async def async_create_helpers(hass: HomeAssistant) -> None:
    """Create all 6 helpers if they don't already exist."""
    await _ensure_input_selects(hass)
    await _ensure_input_numbers(hass)
    await _ensure_input_booleans(hass)


async def async_remove_helpers(hass: HomeAssistant) -> None:
    """Remove all helpers created by this integration."""
    for helper_id in [
        HELPER_P1_MEAT_TYPE,
        HELPER_P2_MEAT_TYPE,
    ]:
        await _delete_helper(hass, "input_select", helper_id)

    for helper_id in [
        HELPER_P1_TARGET_TEMP,
        HELPER_P2_TARGET_TEMP,
    ]:
        await _delete_helper(hass, "input_number", helper_id)

    for helper_id in [
        HELPER_P1_ALERT_SENT,
        HELPER_P2_ALERT_SENT,
    ]:
        await _delete_helper(hass, "input_boolean", helper_id)


# ── Internal helpers ──────────────────────────────────────────────────────────

async def _ensure_input_selects(hass: HomeAssistant) -> None:
    """Create Probe 1 and Probe 2 meat-type dropdowns."""
    component = hass.data.get("input_select")
    if component is None:
        _LOGGER.error("input_select component not loaded — cannot create dropdown helpers")
        return

    for helper_id, name in [
        (HELPER_P1_MEAT_TYPE, "Probe 1 Meat Type"),
        (HELPER_P2_MEAT_TYPE, "Probe 2 Meat Type"),
    ]:
        entity_id = f"input_select.{helper_id}"
        if hass.states.get(entity_id):
            _LOGGER.debug("Helper %s already exists — skipping", entity_id)
            continue
        try:
            await component.storage_collection.async_create_item({
                "id": helper_id,
                "name": name,
                "options": MEAT_OPTIONS,
                "initial": "None",
                "icon": "mdi:food-steak",
            })
            _LOGGER.info("Created helper: %s", entity_id)
        except Exception as err:
            _LOGGER.error("Failed to create %s: %s", entity_id, err)


async def _ensure_input_numbers(hass: HomeAssistant) -> None:
    """Create Probe 1 and Probe 2 target-temp number inputs."""
    component = hass.data.get("input_number")
    if component is None:
        _LOGGER.error("input_number component not loaded — cannot create number helpers")
        return

    for helper_id, name in [
        (HELPER_P1_TARGET_TEMP, "Probe 1 Target Temp"),
        (HELPER_P2_TARGET_TEMP, "Probe 2 Target Temp"),
    ]:
        entity_id = f"input_number.{helper_id}"
        if hass.states.get(entity_id):
            _LOGGER.debug("Helper %s already exists — skipping", entity_id)
            continue
        try:
            await component.storage_collection.async_create_item({
                "id": helper_id,
                "name": name,
                "min": 32,
                "max": 250,
                "step": 1,
                "unit_of_measurement": "°F",
                "mode": "box",
                "icon": "mdi:thermometer-alert",
            })
            _LOGGER.info("Created helper: %s", entity_id)
        except Exception as err:
            _LOGGER.error("Failed to create %s: %s", entity_id, err)


async def _ensure_input_booleans(hass: HomeAssistant) -> None:
    """Create Probe 1 and Probe 2 alert-sent toggles."""
    component = hass.data.get("input_boolean")
    if component is None:
        _LOGGER.error("input_boolean component not loaded — cannot create toggle helpers")
        return

    for helper_id, name in [
        (HELPER_P1_ALERT_SENT, "Probe 1 Alert Sent"),
        (HELPER_P2_ALERT_SENT, "Probe 2 Alert Sent"),
    ]:
        entity_id = f"input_boolean.{helper_id}"
        if hass.states.get(entity_id):
            _LOGGER.debug("Helper %s already exists — skipping", entity_id)
            continue
        try:
            await component.storage_collection.async_create_item({
                "id": helper_id,
                "name": name,
                "initial": False,
                "icon": "mdi:bell-check",
            })
            _LOGGER.info("Created helper: %s", entity_id)
        except Exception as err:
            _LOGGER.error("Failed to create %s: %s", entity_id, err)


async def _delete_helper(hass: HomeAssistant, domain: str, helper_id: str) -> None:
    """Delete a helper from the storage collection."""
    component = hass.data.get(domain)
    if component is None:
        return
    try:
        await component.storage_collection.async_delete_item(helper_id)
        _LOGGER.info("Removed helper: %s.%s", domain, helper_id)
    except Exception as err:
        _LOGGER.debug("Could not remove %s.%s (may not exist): %s", domain, helper_id, err)
