"""
Create and remove all 18 Traeger Cook Guide automations.

Writes directly to HA's automation storage collection — the same backend the UI
uses — so automations appear in Settings → Automations, are fully editable, and
survive restarts. Stable IDs prevent duplicates on re-install.

Per probe (×4):
  • Set Target      — meat type selected → set that probe's target temp
  • Almost Done     — within 10°F of target → push notification
  • Target Reached  — hits target → push notification (once)
  • Reset Alert     — meat type set back to None → clear the alert flag
Pit (×2):
  • Pit Running Hot — active pit probe drifts above target + PIT_BAND
  • Pit Fire Drop   — active pit probe drifts below target − PIT_BAND
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant

from .const import (
    AUTOMATION_IDS,
    PROBES,
    PIT_BAND,
    PIT_TARGET_DEFAULT,
    ENTITY_PROBE_TEMP,
    HELPER_PIT_PROBE,
    HELPER_PIT_TARGET,
    meat_type_id,
    target_temp_id,
    alert_sent_id,
)

_LOGGER = logging.getLogger(__name__)

# Maps the selected meat type to a target internal temp. Mirrors MEAT_OPTIONS.
_MEAT_TARGET_TEMPLATE = """\
{% set m = trigger.to_state.state %}
{% if m == 'Brisket' %}203
{% elif m == 'Beef Ribs' %}205
{% elif m == 'Pork Ribs' %}195
{% elif m == 'Pulled Pork' %}205
{% elif m == 'Beef Rare' %}125
{% elif m == 'Beef Medium Rare' %}133
{% elif m == 'Beef Medium' %}140
{% elif m == 'Beef Medium Well' %}150
{% elif m == 'Beef Well Done' %}160
{% elif m == 'Chicken Breast' %}157
{% elif m == 'Chicken Well Done' %}170
{% elif m == 'Salmon Medium' %}125
{% elif m == 'Salmon Well Done' %}145
{% elif m == 'Lean Fish' %}145
{% else %}165{% endif %}\
"""

# Entities for the pit block.
_PIT_SEL = f"input_select.{HELPER_PIT_PROBE}"
_PIT_NUM = f"input_number.{HELPER_PIT_TARGET}"
# Jinja expression that resolves the active pit probe's live temperature.
# "P3" -> sensor.govee_meat_thermometer_temperature_probe_3 ; -999 if none/unavailable.
_PIT_TEMP = (
    "states('sensor.govee_meat_thermometer_temperature_probe_' ~ "
    f"states('{_PIT_SEL}')[1:]) | float(-999)"
)


def _build_automations() -> list[dict[str, Any]]:
    """Return the list of all 18 automation config dicts."""

    def set_target(n: int) -> dict:
        sel = f"input_select.{meat_type_id(n)}"
        num = f"input_number.{target_temp_id(n)}"
        flag = f"input_boolean.{alert_sent_id(n)}"
        return {
            "id": AUTOMATION_IDS[f"p{n}_set_target"],
            "alias": f"Traeger Probe {n} Set Target",
            "description": f"Auto-sets target temp when Probe {n} meat type is selected",
            "mode": "single",
            "trigger": [{"platform": "state", "entity_id": sel}],
            "condition": [],
            "action": [
                {"action": "input_boolean.turn_off", "target": {"entity_id": flag}},
                {
                    "action": "input_number.set_value",
                    "target": {"entity_id": num},
                    "data": {"value": _MEAT_TARGET_TEMPLATE},
                },
            ],
        }

    def almost_done(n: int) -> dict:
        temp_e = ENTITY_PROBE_TEMP[n]
        num = f"input_number.{target_temp_id(n)}"
        flag = f"input_boolean.{alert_sent_id(n)}"
        sel = f"input_select.{meat_type_id(n)}"
        return {
            "id": AUTOMATION_IDS[f"p{n}_almost_done"],
            "alias": f"Traeger Probe {n} Almost Done",
            "description": f"Sends push alert when Probe {n} is within 10°F of target",
            "mode": "single",
            "trigger": [
                {
                    "platform": "template",
                    "value_template": (
                        f"{{{{ states('{temp_e}') | float(0) >= "
                        f"(states('{num}') | float(999) - 10) }}}}"
                    ),
                }
            ],
            "condition": [
                {"condition": "state", "entity_id": flag, "state": "off"},
                {
                    "condition": "not",
                    "conditions": [
                        {"condition": "state", "entity_id": sel, "state": "None"}
                    ],
                },
            ],
            "action": [
                {
                    "action": "notify.notify",
                    "data": {
                        "title": f"⚠️ Probe {n} Almost Done",
                        "message": (
                            f"{{{{ states('{sel}') }}}} is at "
                            f"{{{{ states('{temp_e}') }}}}°F — "
                            f"{{{{ (states('{num}') | float - "
                            f"states('{temp_e}') | float) | int }}}}°F to go!"
                        ),
                    },
                }
            ],
        }

    def target_reached(n: int) -> dict:
        temp_e = ENTITY_PROBE_TEMP[n]
        num = f"input_number.{target_temp_id(n)}"
        flag = f"input_boolean.{alert_sent_id(n)}"
        sel = f"input_select.{meat_type_id(n)}"
        return {
            "id": AUTOMATION_IDS[f"p{n}_target_reached"],
            "alias": f"Traeger Probe {n} Target Reached",
            "description": f"Fires once when Probe {n} hits target temp",
            "mode": "single",
            "trigger": [
                {
                    "platform": "template",
                    "value_template": (
                        f"{{{{ states('{temp_e}') | float(0) >= "
                        f"states('{num}') | float(999) }}}}"
                    ),
                }
            ],
            "condition": [
                {"condition": "state", "entity_id": flag, "state": "off"},
                {
                    "condition": "not",
                    "conditions": [
                        {"condition": "state", "entity_id": sel, "state": "None"}
                    ],
                },
            ],
            "action": [
                {"action": "input_boolean.turn_on", "target": {"entity_id": flag}},
                {
                    "action": "notify.notify",
                    "data": {
                        "title": f"🍖 Probe {n} Ready!",
                        "message": (
                            f"{{{{ states('{sel}') }}}} hit "
                            f"{{{{ states('{temp_e}') }}}}°F — pull it now!"
                        ),
                        "data": {"push": {"sound": "default"}},
                    },
                },
            ],
        }

    def reset_alert(n: int) -> dict:
        sel = f"input_select.{meat_type_id(n)}"
        flag = f"input_boolean.{alert_sent_id(n)}"
        return {
            "id": AUTOMATION_IDS[f"p{n}_reset_alert"],
            "alias": f"Traeger Reset Probe {n} Alert",
            "description": f"Resets alert flag when Probe {n} set back to None",
            "mode": "single",
            "trigger": [{"platform": "state", "entity_id": sel, "to": "None"}],
            "condition": [],
            "action": [
                {"action": "input_boolean.turn_off", "target": {"entity_id": flag}}
            ],
        }

    # ── Pit drift automations ────────────────────────────────────────────────
    # The active pit probe is dynamic (chosen via input_select.pit_probe), so the
    # trigger resolves the right temp sensor at evaluation time. `for` debounces
    # brief spikes (lid open, spritz) so we only alert on a real drift.
    def pit_high() -> dict:
        value_template = (
            "{% set p = states('" + _PIT_SEL + "') %}"
            "{% if p in ['P1','P2','P3','P4'] %}"
            "{% set t = " + _PIT_TEMP + " %}"
            "{{ t > -900 and t > (states('" + _PIT_NUM + "') | float("
            + str(PIT_TARGET_DEFAULT) + ") + " + str(PIT_BAND) + ") }}"
            "{% else %}false{% endif %}"
        )
        message = (
            "Pit is at {{ " + _PIT_TEMP + " | round(0) }}°F — target "
            "{{ states('" + _PIT_NUM + "') }}°F. Check for a flare-up."
        )
        return {
            "id": AUTOMATION_IDS["pit_high"],
            "alias": "Traeger Pit Running Hot",
            "description": "Alerts when the active pit probe drifts above target",
            "mode": "single",
            "trigger": [
                {"platform": "template", "value_template": value_template, "for": {"seconds": 30}}
            ],
            "condition": [],
            "action": [
                {
                    "action": "notify.notify",
                    "data": {"title": "🔥 Pit Running Hot", "message": message},
                }
            ],
        }

    def pit_low() -> dict:
        value_template = (
            "{% set p = states('" + _PIT_SEL + "') %}"
            "{% if p in ['P1','P2','P3','P4'] %}"
            "{% set t = " + _PIT_TEMP + " %}"
            "{{ t > -900 and t < (states('" + _PIT_NUM + "') | float("
            + str(PIT_TARGET_DEFAULT) + ") - " + str(PIT_BAND) + ") }}"
            "{% else %}false{% endif %}"
        )
        message = (
            "Pit dropped to {{ " + _PIT_TEMP + " | round(0) }}°F — target "
            "{{ states('" + _PIT_NUM + "') }}°F. Fire may be dying."
        )
        return {
            "id": AUTOMATION_IDS["pit_low"],
            "alias": "Traeger Pit Fire Dropping",
            "description": "Alerts when the active pit probe drifts below target",
            "mode": "single",
            "trigger": [
                {"platform": "template", "value_template": value_template, "for": {"seconds": 60}}
            ],
            "condition": [],
            "action": [
                {
                    "action": "notify.notify",
                    "data": {"title": "❄️ Pit Fire Dropping", "message": message},
                }
            ],
        }

    autos: list[dict[str, Any]] = []
    for n in PROBES:
        autos.append(set_target(n))
        autos.append(almost_done(n))
        autos.append(target_reached(n))
        autos.append(reset_alert(n))
    autos.append(pit_high())
    autos.append(pit_low())
    return autos


async def async_create_automations(hass: HomeAssistant) -> None:
    """Write all 18 automations into HA's storage collection."""
    component = hass.data.get("automation")
    if component is None:
        _LOGGER.error("automation component not loaded — cannot register automations")
        return

    collection = getattr(component, "storage_collection", None)
    if collection is None:
        _LOGGER.error("automation storage_collection not found")
        return

    existing_ids = {item["id"] for item in collection.async_items()}

    for auto in _build_automations():
        auto_id = auto["id"]
        if auto_id in existing_ids:
            _LOGGER.debug("Automation %s already exists — skipping", auto_id)
            continue
        try:
            await collection.async_create_item(auto)
            _LOGGER.info("Created automation: %s (%s)", auto["alias"], auto_id)
        except Exception as err:
            _LOGGER.error("Failed to create automation %s: %s", auto_id, err)


async def async_remove_automations(hass: HomeAssistant) -> None:
    """Remove all automations created by this integration."""
    component = hass.data.get("automation")
    if component is None:
        return

    collection = getattr(component, "storage_collection", None)
    if collection is None:
        return

    stable_ids = set(AUTOMATION_IDS.values())
    for item in list(collection.async_items()):
        if item.get("id") in stable_ids:
            try:
                await collection.async_delete_item(item["id"])
                _LOGGER.info("Removed automation: %s", item.get("alias", item["id"]))
            except Exception as err:
                _LOGGER.debug("Could not remove automation %s: %s", item["id"], err)
