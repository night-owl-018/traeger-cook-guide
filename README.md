# 🔥 Traeger Cook Guide for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A zero-touch HACS integration that installs a full interactive Traeger smoker cook guide into your Home Assistant. Browse 60+ foods with smoker temps, cook times, and internal targets — click any food to assign it to your HOPEPOP wireless meat thermometer probe. HA automatically handles the rest: sets target temp, sends a push alert at 10°F out, and fires another when it's ready to pull.

## What gets installed automatically

When you click **Submit** in the integration setup:

| What | Details |
|------|---------|
| 📄 Cook guide HTML | Copied to `/config/www/traeger_cook_guide/` |
| 🔧 6 helpers | 2 dropdowns, 2 number inputs, 2 toggles |
| ⚡ 9 automations | Set target, warn, alert, reset, battery low |
| 📋 Notification | Dashboard card YAML to paste (1 manual step) |

## Requirements

- Home Assistant 2024.1+
- HACS installed
- HOPEPOP thermometer flashed with ESPHome + BT proxy producing these entity IDs:
  - `sensor.bt_proxy_hopepop_probe_1_temp`
  - `sensor.bt_proxy_hopepop_probe_2_temp`
  - `sensor.bt_proxy_hopepop_probe_1_battery`
  - `sensor.bt_proxy_hopepop_probe_2_battery`
  - `sensor.bt_proxy_hopepop_base_battery`
  - `binary_sensor.bt_proxy_hopepop_connected`
  - `binary_sensor.bt_proxy_hopepop_probes_charging`

## Installation

### Step 1 — Add to HACS (one time)

1. In HA, go to **HACS → ⋮ menu (top right) → Custom repositories**
2. Repository URL: `https://github.com/night-owl-018/traeger-cook-guide`
3. Category: **Integration** → Click **Add**
4. Search HACS for **Traeger Cook Guide** → **Download** → **Restart Home Assistant**

### Step 2 — Add the integration

1. **Settings → Devices & Services → + Add Integration**
2. Search **Traeger Cook Guide** → click it → click **Submit**
3. Done — helpers and automations are created automatically

### Step 3 — Add the dashboard card

A notification will appear after setup. Copy the YAML from it and paste it as a **Manual** card on your dashboard. That's the only thing you do manually.

### Step 4 — Authenticate the cook guide (one time per browser)

1. **Profile → Long-Lived Access Tokens → Create Token** → name it `Traeger Cook Guide`
2. Open the guide → paste the token when prompted → it's saved, never asked again

## Uninstall

Remove the integration from **Settings → Devices & Services** — helpers, automations, and www files are cleaned up automatically.

## Repository structure

```
traeger-cook-guide/
├── hacs.json
├── README.md
├── www/
│   └── traeger_cook_guide.html     ← interactive cook guide
└── custom_components/
    └── traeger_cook_guide/
        ├── __init__.py             ← orchestrates setup/teardown
        ├── manifest.json
        ├── config_flow.py          ← one-click install UI
        ├── const.py                ← all entity IDs and constants
        ├── helpers.py              ← creates 6 HA helpers
        ├── automations.py          ← creates 9 HA automations
        ├── www_install.py          ← copies HTML to /config/www/
        └── strings.json
```
