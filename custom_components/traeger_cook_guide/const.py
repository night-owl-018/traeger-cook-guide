"""Constants for Traeger Cook Guide."""
from __future__ import annotations

DOMAIN = "traeger_cook_guide"
VERSION = "2.4.1"

# Probe numbers this integration manages (Govee H5198 has four).
PROBES = (1, 2, 3, 4)

# ── Govee H5198 entity IDs ────────────────────────────────────────────────────
# Provided by the Govee integration — read-only. If your integration names these
# differently, change them here (and in the ENT map in traeger_cook_guide.html).
ENTITY_PROBE_TEMP = {
    n: f"sensor.govee_meat_thermometer_temperature_probe_{n}" for n in PROBES
}
ENTITY_PROBE_ALARM = {
    n: f"sensor.govee_meat_thermometer_temperature_alarm_probe_{n}" for n in PROBES
}
ENTITY_PROBE_LOW_ALARM = {
    n: f"sensor.govee_meat_thermometer_low_temperature_alarm_probe_{n}" for n in PROBES
}

# ── Helper object_id templates (created by this integration) ──────────────────
HELPER_MEAT_TYPE = "probe_{n}_meat_type"      # input_select, per probe
HELPER_TARGET_TEMP = "probe_{n}_target_temp"  # input_number, per probe
HELPER_ALERT_SENT = "probe_{n}_alert_sent"    # input_boolean, per probe
HELPER_PIT_PROBE = "pit_probe"                # input_select, which probe watches the pit
HELPER_PIT_TARGET = "pit_target_temp"         # input_number, pit hold temp


def meat_type_id(n: int) -> str:
    """object_id for a probe's meat-type dropdown."""
    return HELPER_MEAT_TYPE.format(n=n)


def target_temp_id(n: int) -> str:
    """object_id for a probe's target-temp number."""
    return HELPER_TARGET_TEMP.format(n=n)


def alert_sent_id(n: int) -> str:
    """object_id for a probe's alert-sent toggle."""
    return HELPER_ALERT_SENT.format(n=n)


# ── Pit / grill monitoring ────────────────────────────────────────────────────
PIT_OPTIONS = ["Off", "P1", "P2", "P3", "P4"]  # pit_probe dropdown choices
PIT_BAND = 25                                   # °F of drift before a hot/cold pit alert
PIT_TARGET_DEFAULT = 225                        # default pit hold temp

# ── Meat-type dropdown options (shared by all four probes) ────────────────────
MEAT_OPTIONS = [
    "None",
    "Brisket",
    "Beef Ribs",
    "Pork Ribs",
    "Pulled Pork",
    "Beef Rare",
    "Beef Medium Rare",
    "Beef Medium",
    "Beef Medium Well",
    "Beef Well Done",
    "Chicken Breast",
    "Chicken Well Done",
    "Salmon Medium",
    "Salmon Well Done",
    "Lean Fish",
]

# ── Automation IDs — stable so re-installs don't duplicate ────────────────────
# 4 per probe (set target / almost done / target reached / reset) + 2 pit drift = 18
AUTOMATION_IDS: dict[str, str] = {}
for _n in PROBES:
    AUTOMATION_IDS[f"p{_n}_set_target"] = f"traeger_cook_guide_p{_n}_set_target"
    AUTOMATION_IDS[f"p{_n}_almost_done"] = f"traeger_cook_guide_p{_n}_almost_done"
    AUTOMATION_IDS[f"p{_n}_target_reached"] = f"traeger_cook_guide_p{_n}_target_reached"
    AUTOMATION_IDS[f"p{_n}_reset_alert"] = f"traeger_cook_guide_p{_n}_reset_alert"
AUTOMATION_IDS["pit_high"] = "traeger_cook_guide_pit_high"
AUTOMATION_IDS["pit_low"] = "traeger_cook_guide_pit_low"

WWW_SUBDIR = "traeger_cook_guide"
HTML_FILENAME = "traeger_cook_guide.html"
