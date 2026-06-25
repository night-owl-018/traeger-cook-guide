"""
Create and remove all 9 Traeger Cook Guide automations.

Writes directly to HA's automation storage collection — the same backend
the UI uses — so automations appear in Settings → Automations, are fully
editable, and survive restarts.  Stable IDs prevent duplicates on re-install.
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant

from .const import (
    AUTOMATION_IDS,
    ENTITY_PROBE_1_TEMP,
    ENTITY_PROBE_2_TEMP,
    ENTITY_PROBE_1_BATTERY,
    ENTITY_PROBE_2_BATTERY,
    ENTITY_BASE_BATTERY,
    HELPER_P1_MEAT_TYPE,
    HELPER_P2_MEAT_TYPE,
    HELPER_P1_TARGET_TEMP,
    HELPER_P2_TARGET_TEMP,
    HELPER_P1_ALERT_SENT,
    HELPER_P2_ALERT_SENT,
)

_LOGGER = logging.getLogger(__name__)

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


def _build_automations() -> list[dict[str, Any]]:
    """Return the list of all 9 automation config dicts."""

    def set_target(probe: int) -> dict:
        sel = f"input_select.{HELPER_P1_MEAT_TYPE if probe == 1 else HELPER_P2_MEAT_TYPE}"
        num = f"input_number.{HELPER_P1_TARGET_TEMP if probe == 1 else HELPER_P2_TARGET_TEMP}"
        flag = f"input_boolean.{HELPER_P1_ALERT_SENT if probe == 1 else HELPER_P2_ALERT_SENT}"
        key = f"p{probe}_set_target"
        return {
            "id": AUTOMATION_IDS[key],
            "alias": f"Traeger Probe {probe} Set Target",
            "description": f"Auto-sets target temp when Probe {probe} meat type is selected",
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

    def almost_done(probe: int) -> dict:
        temp_e = ENTITY_PROBE_1_TEMP if probe == 1 else ENTITY_PROBE_2_TEMP
        tgt_e = f"input_number.{HELPER_P1_TARGET_TEMP if probe == 1 else HELPER_P2_TARGET_TEMP}"
        flag_e = f"input_boolean.{HELPER_P1_ALERT_SENT if probe == 1 else HELPER_P2_ALERT_SENT}"
        sel_e = f"input_select.{HELPER_P1_MEAT_TYPE if probe == 1 else HELPER_P2_MEAT_TYPE}"
        key = f"p{probe}_almost_done"
        return {
            "id": AUTOMATION_IDS[key],
            "alias": f"Traeger Probe {probe} Almost Done",
            "description": f"Sends push alert when Probe {probe} is within 10°F of target",
            "mode": "single",
            "trigger": [
                {
                    "platform": "template",
                    "value_template": (
                        f"{{{{ states('{temp_e}') | float(0) >= "
                        f"(states('{tgt_e}') | float(999) - 10) }}}}"
                    ),
                }
            ],
            "condition": [
                {"condition": "state", "entity_id": flag_e, "state": "off"},
                {
                    "condition": "not",
                    "conditions": [
                        {"condition": "state", "entity_id": sel_e, "state": "None"}
                    ],
                },
            ],
            "action": [
                {
                    "action": "notify.notify",
                    "data": {
                        "title": f"⚠️ Probe {probe} Almost Done",
                        "message": (
                            f"{{{{ states('{sel_e}') }}}} is at "
                            f"{{{{ states('{temp_e}') }}}}°F — "
                            f"{{{{ (states('{tgt_e}') | float - "
                            f"states('{temp_e}') | float) | int }}}}°F to go!"
                        ),
                    },
                }
            ],
        }

    def target_reached(probe: int) -> dict:
        temp_e = ENTITY_PROBE_1_TEMP if probe == 1 else ENTITY_PROBE_2_TEMP
        tgt_e = f"input_number.{HELPER_P1_TARGET_TEMP if probe == 1 else HELPER_P2_TARGET_TEMP}"
        flag_e = f"input_boolean.{HELPER_P1_ALERT_SENT if probe == 1 else HELPER_P2_ALERT_SENT}"
        sel_e = f"input_select.{HELPER_P1_MEAT_TYPE if probe == 1 else HELPER_P2_MEAT_TYPE}"
        key = f"p{probe}_target_reached"
        return {
            "id": AUTOMATION_IDS[key],
            "alias": f"Traeger Probe {probe} Target Reached",
            "description": f"Fires once when Probe {probe} hits target temp",
            "mode": "single",
            "trigger": [
                {
                    "platform": "template",
                    "value_template": (
                        f"{{{{ states('{temp_e}') | float(0) >= "
                        f"states('{tgt_e}') | float(999) }}}}"
                    ),
                }
            ],
            "condition": [
                {"condition": "state", "entity_id": flag_e, "state": "off"},
                {
                    "condition": "not",
                    "conditions": [
                        {"condition": "state", "entity_id": sel_e, "state": "None"}
                    ],
                },
            ],
            "action": [
                {"action": "input_boolean.turn_on", "target": {"entity_id": flag_e}},
                {
                    "action": "notify.notify",
                    "data": {
                        "title": f"🍖 Probe {probe} Ready!",
                        "message": (
                            f"{{{{ states('{sel_e}') }}}} hit "
                            f"{{{{ states('{temp_e}') }}}}°F — pull it now!"
                        ),
                        "data": {"push": {"sound": "default"}},
                    },
                },
            ],
        }

    def reset_alert(probe: int) -> dict:
        sel_e = f"input_select.{HELPER_P1_MEAT_TYPE if probe == 1 else HELPER_P2_MEAT_TYPE}"
        flag_e = f"input_boolean.{HELPER_P1_ALERT_SENT if probe == 1 else HELPER_P2_ALERT_SENT}"
        key = f"p{probe}_reset_alert"
        return {
            "id": AUTOMATION_IDS[key],
            "alias": f"Traeger Reset Probe {probe} Alert",
            "description": f"Resets alert flag when Probe {probe} set back to None",
            "mode": "single",
            "trigger": [{"platform": "state", "entity_id": sel_e, "to": "None"}],
            "condition": [],
            "action": [
                {"action": "input_boolean.turn_off", "target": {"entity_id": flag_e}}
            ],
        }

    battery_low = {
        "id": AUTOMATION_IDS["battery_low"],
        "alias": "Traeger Battery Low",
        "description": "Alerts when any probe or base drops below threshold",
        "mode": "single",
        "trigger": [
            {"platform": "numeric_state", "entity_id": ENTITY_PROBE_1_BATTERY, "below": 25},
            {"platform": "numeric_state", "entity_id": ENTITY_PROBE_2_BATTERY, "below": 25},
            {"platform": "numeric_state", "entity_id": ENTITY_BASE_BATTERY, "below": 20},
        ],
        "condition": [],
        "action": [
            {
                "action": "notify.notify",
                "data": {
                    "title": "🔋 HOPEPOP Battery Low",
                    "message": (
                        f"{{% if trigger.entity_id == '{ENTITY_PROBE_1_BATTERY}' %}}"
                        f"Probe 1 at {{{{ states('{ENTITY_PROBE_1_BATTERY}') }}}}%"
                        f"{{% elif trigger.entity_id == '{ENTITY_PROBE_2_BATTERY}' %}}"
                        f"Probe 2 at {{{{ states('{ENTITY_PROBE_2_BATTERY}') }}}}%"
                        f"{{% else %}}Base at {{{{ states('{ENTITY_BASE_BATTERY}') }}}}%{{% endif %}}"
                        " — charge before your next cook"
                    ),
                },
            }
        ],
    }

    return [
        set_target(1),
        set_target(2),
        almost_done(1),
        almost_done(2),
        target_reached(1),
        target_reached(2),
        reset_alert(1),
        reset_alert(2),
        battery_low,
    ]


async def async_create_automations(hass: HomeAssistant) -> None:
    """Write all 9 automations into HA's storage collection."""
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
