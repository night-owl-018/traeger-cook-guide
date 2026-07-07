"""
Create and remove the 14 HA helpers that power the Traeger Cook Guide.

Uses the same internal StorageCollection API that the HA UI uses, so helpers
appear in Settings → Helpers, are editable in the UI, and survive restarts —
exactly as if the user created them by hand.

  Per probe (×4):  input_select.probe_N_meat_type
                   input_number.probe_N_target_temp
                   input_boolean.probe_N_alert_sent
  Pit control:     input_select.pit_probe
                   input_number.pit_target_temp
"""
from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant

from .const import (
    PROBES,
    MEAT_OPTIONS,
    PIT_OPTIONS,
    PIT_TARGET_DEFAULT,
    HELPER_PIT_PROBE,
    HELPER_PIT_TARGET,
    meat_type_id,
    target_temp_id,
    alert_sent_id,
)

_LOGGER = logging.getLogger(__name__)


async def async_create_helpers(hass: HomeAssistant) -> None:
    """Create all 14 helpers if they don't already exist."""
    await _ensure_input_selects(hass)
    await _ensure_input_numbers(hass)
    await _ensure_input_booleans(hass)
    await _ensure_pit_helpers(hass)


async def async_remove_helpers(hass: HomeAssistant) -> None:
    """Remove all helpers created by this integration."""
    for n in PROBES:
        await _delete_helper(hass, "input_select", meat_type_id(n))
        await _delete_helper(hass, "input_number", target_temp_id(n))
        await _delete_helper(hass, "input_boolean", alert_sent_id(n))
    await _delete_helper(hass, "input_select", HELPER_PIT_PROBE)
    await _delete_helper(hass, "input_number", HELPER_PIT_TARGET)


# ── Internal helpers ──────────────────────────────────────────────────────────

async def _ensure_input_selects(hass: HomeAssistant) -> None:
    """Create the four probe meat-type dropdowns."""
    component = hass.data.get("input_select")
    if component is None:
        _LOGGER.error("input_select component not loaded — cannot create dropdown helpers")
        return

    for n in PROBES:
        helper_id = meat_type_id(n)
        if hass.states.get(f"input_select.{helper_id}"):
            _LOGGER.debug("Helper input_select.%s already exists — skipping", helper_id)
            continue
        try:
            await component.storage_collection.async_create_item({
                "id": helper_id,
                "name": f"Probe {n} Meat Type",
                "options": MEAT_OPTIONS,
                "initial": "None",
                "icon": "mdi:food-steak",
            })
            _LOGGER.info("Created helper: input_select.%s", helper_id)
        except Exception as err:
            _LOGGER.error("Failed to create input_select.%s: %s", helper_id, err)


async def _ensure_input_numbers(hass: HomeAssistant) -> None:
    """Create the four probe target-temp number inputs."""
    component = hass.data.get("input_number")
    if component is None:
        _LOGGER.error("input_number component not loaded — cannot create number helpers")
        return

    for n in PROBES:
        helper_id = target_temp_id(n)
        if hass.states.get(f"input_number.{helper_id}"):
            _LOGGER.debug("Helper input_number.%s already exists — skipping", helper_id)
            continue
        try:
            await component.storage_collection.async_create_item({
                "id": helper_id,
                "name": f"Probe {n} Target Temp",
                "min": 32,
                "max": 250,
                "step": 1,
                "unit_of_measurement": "°F",
                "mode": "box",
                "icon": "mdi:thermometer-alert",
            })
            _LOGGER.info("Created helper: input_number.%s", helper_id)
        except Exception as err:
            _LOGGER.error("Failed to create input_number.%s: %s", helper_id, err)


async def _ensure_input_booleans(hass: HomeAssistant) -> None:
    """Create the four probe alert-sent toggles."""
    component = hass.data.get("input_boolean")
    if component is None:
        _LOGGER.error("input_boolean component not loaded — cannot create toggle helpers")
        return

    for n in PROBES:
        helper_id = alert_sent_id(n)
        if hass.states.get(f"input_boolean.{helper_id}"):
            _LOGGER.debug("Helper input_boolean.%s already exists — skipping", helper_id)
            continue
        try:
            await component.storage_collection.async_create_item({
                "id": helper_id,
                "name": f"Probe {n} Alert Sent",
                "initial": False,
                "icon": "mdi:bell-check",
            })
            _LOGGER.info("Created helper: input_boolean.%s", helper_id)
        except Exception as err:
            _LOGGER.error("Failed to create input_boolean.%s: %s", helper_id, err)


async def _ensure_pit_helpers(hass: HomeAssistant) -> None:
    """Create the pit-probe selector and pit target-temp number."""
    select_comp = hass.data.get("input_select")
    if select_comp is not None and not hass.states.get(f"input_select.{HELPER_PIT_PROBE}"):
        try:
            await select_comp.storage_collection.async_create_item({
                "id": HELPER_PIT_PROBE,
                "name": "Pit Probe",
                "options": PIT_OPTIONS,
                "initial": "Off",
                "icon": "mdi:grill",
            })
            _LOGGER.info("Created helper: input_select.%s", HELPER_PIT_PROBE)
        except Exception as err:
            _LOGGER.error("Failed to create input_select.%s: %s", HELPER_PIT_PROBE, err)

    number_comp = hass.data.get("input_number")
    if number_comp is not None and not hass.states.get(f"input_number.{HELPER_PIT_TARGET}"):
        try:
            await number_comp.storage_collection.async_create_item({
                "id": HELPER_PIT_TARGET,
                "name": "Pit Target Temp",
                "min": 100,
                "max": 700,
                "step": 5,
                "initial": PIT_TARGET_DEFAULT,
                "unit_of_measurement": "°F",
                "mode": "box",
                "icon": "mdi:thermometer",
            })
            _LOGGER.info("Created helper: input_number.%s", HELPER_PIT_TARGET)
        except Exception as err:
            _LOGGER.error("Failed to create input_number.%s: %s", HELPER_PIT_TARGET, err)


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
