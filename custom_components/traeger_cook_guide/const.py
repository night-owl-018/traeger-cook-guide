"""Constants for Traeger Cook Guide."""

DOMAIN = "traeger_cook_guide"
VERSION = "1.4.5"

# ESPHome BT proxy entity IDs — must match your ESPHome config
ENTITY_PROBE_1_TEMP    = "sensor.bt_proxy_hopepop_probe_1_temp"
ENTITY_PROBE_2_TEMP    = "sensor.bt_proxy_hopepop_probe_2_temp"
ENTITY_PROBE_1_BATTERY = "sensor.bt_proxy_hopepop_probe_1_battery"
ENTITY_PROBE_2_BATTERY = "sensor.bt_proxy_hopepop_probe_2_battery"
ENTITY_BASE_BATTERY    = "sensor.bt_proxy_hopepop_base_battery"
ENTITY_CONNECTED       = "binary_sensor.bt_proxy_hopepop_connected"
ENTITY_CHARGING        = "binary_sensor.bt_proxy_hopepop_probes_charging"

# Helpers this integration creates
HELPER_P1_MEAT_TYPE    = "probe_1_meat_type"
HELPER_P2_MEAT_TYPE    = "probe_2_meat_type"
HELPER_P1_TARGET_TEMP  = "probe_1_target_temp"
HELPER_P2_TARGET_TEMP  = "probe_2_target_temp"
HELPER_P1_ALERT_SENT   = "probe_1_alert_sent"
HELPER_P2_ALERT_SENT   = "probe_2_alert_sent"

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

# Automation IDs — stable so re-installs don't duplicate
AUTOMATION_IDS = {
    "p1_set_target":      "traeger_cook_guide_p1_set_target",
    "p2_set_target":      "traeger_cook_guide_p2_set_target",
    "p1_almost_done":     "traeger_cook_guide_p1_almost_done",
    "p2_almost_done":     "traeger_cook_guide_p2_almost_done",
    "p1_target_reached":  "traeger_cook_guide_p1_target_reached",
    "p2_target_reached":  "traeger_cook_guide_p2_target_reached",
    "p1_reset_alert":     "traeger_cook_guide_p1_reset_alert",
    "p2_reset_alert":     "traeger_cook_guide_p2_reset_alert",
    "battery_low":        "traeger_cook_guide_battery_low",
}

WWW_SUBDIR    = "traeger_cook_guide"
HTML_FILENAME = "traeger_cook_guide.html"
