# 🔥 Traeger Cook Guide for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/badge/version-1.3.0-blue.svg)](https://github.com/night-owl-018/traeger-cook-guide/releases)
[![HA](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-brightgreen.svg)](https://www.home-assistant.io)

A zero-touch HACS integration that installs a full interactive Traeger smoker cook guide into your Home Assistant. Browse 60+ foods with smoker temps, cook times, and internal targets — tap any food to assign it to your HOPEPOP wireless meat thermometer probe. HA automatically handles the rest: sets target temp, sends a push alert at 10°F out, and fires another when it's ready to pull.

---

## Features

- 🍖 **60+ foods** across 8 categories — Beef, Pork, Poultry, Seafood, Lamb, Vegetables, Sides, Desserts
- 📱 **Mobile-first design** — compact rows, tap to expand details, no side scrolling
- 🌡️ **Live probe temps** — real-time display with progress bar (green → amber → red)
- 🔔 **Push notifications** — alert at 10°F from target and again when done, broadcasts to all HA users/devices via `notify.notify`
- 📡 **Device status bar** — connection, charging status, and battery % for base unit + both probes
- ✍️ **Custom food builder** — add your own cuts with target temp, cook time, and notes; persists across page refreshes via localStorage
- 🌙 **Dark mode** — automatic, follows system preference
- 🔁 **One-click probe assignment** — sets HA helpers and target temp instantly via WebSocket
- 🔒 **Token persistence** — enter your HA token once per browser, never asked again

---

## What gets installed automatically

When you click **Submit** in the integration setup:

| What | Details |
|------|---------|
| 📄 Cook guide HTML | Copied to `/config/www/traeger_cook_guide/` |
| 🔧 6 helpers | 2 dropdowns, 2 number inputs, 2 toggles |
| ⚡ 9 automations | Set target, warn at 10°F, alert at target, reset, battery low |
| 📋 Notification | Dashboard card YAML to paste (1 manual step) |

---

## Requirements

- Home Assistant 2024.1+
- HACS installed
- HOPEPOP wireless meat thermometer flashed with ESPHome + BT proxy, producing these entity IDs:

| Entity ID | What it is |
|-----------|-----------|
| `sensor.bt_proxy_hopepop_probe_1_temp` | Probe 1 live temperature |
| `sensor.bt_proxy_hopepop_probe_2_temp` | Probe 2 live temperature |
| `sensor.bt_proxy_hopepop_probe_1_battery` | Probe 1 battery % |
| `sensor.bt_proxy_hopepop_probe_2_battery` | Probe 2 battery % |
| `sensor.bt_proxy_hopepop_base_battery` | Base unit battery % |
| `binary_sensor.bt_proxy_hopepop_connected` | BT connection status |
| `binary_sensor.bt_proxy_hopepop_probes_charging` | Charging status |

---

## Installation

### Step 1 — Add to HACS

1. **HACS → ⋮ menu (top right) → Custom repositories**
2. Repository URL: `https://github.com/night-owl-018/traeger-cook-guide`
3. Category: **Integration** → Click **Add**
4. Search HACS for **Traeger Cook Guide** → **Download** → **Restart Home Assistant**

### Step 2 — Add the integration

1. **Settings → Devices & Services → + Add Integration**
2. Search **Traeger Cook Guide** → click it → click **Submit**
3. Helpers and automations are created automatically on first run

### Step 3 — Add the dashboard card

A persistent notification will appear after setup with the YAML. Add it as a **Manual** card on your dashboard:

```yaml
type: iframe
url: /local/traeger_cook_guide/traeger_cook_guide.html
aspect_ratio: "100%"
title: Traeger Cook Guide
```

> **HTTPS users (DuckDNS, Nabu Casa, etc.):** If the iframe shows blank, add this to `configuration.yaml` under the `http:` section and restart HA:
> ```yaml
> http:
>   use_x_frame_options: false
> ```
> This is safe for personal home setups. The setting prevents clickjacking but the risk is negligible for a single-user home lab.

### Step 4 — Authenticate the cook guide

1. **Profile → Long-Lived Access Tokens → Create Token** → name it `Traeger Cook Guide`
2. Open the cook guide — it will prompt for the token on first load
3. Token is saved to `localStorage` — never asked again on that browser/device

**To skip the prompt on ALL devices permanently**, open the HTML file on your HA server and find this line near the top of the JavaScript:
```javascript
const HA_TOKEN = "";
```
Paste your token between the quotes:
```javascript
const HA_TOKEN = "eyJ0eXAiOiJKV1Q...your_full_token_here";
```
File location on most setups:
```
/config/www/traeger_cook_guide/traeger_cook_guide.html
```

---

## How it works

### One-click assignment flow

1. Tap any food row → tap **P1** or **P2**
2. The guide sends three calls to HA via WebSocket:
   - Sets `input_select.probe_X_meat_type` → triggers automation to set target temp
   - Sets `input_number.probe_X_target_temp` directly as backup
   - Resets `input_boolean.probe_X_alert_sent` to off
3. HA automations take over from there

### Notification flow

| Event | What fires |
|-------|-----------|
| Probe reaches target − 10°F | ⚠️ "Almost Done" push to all devices |
| Probe reaches target | 🍖 "Ready to pull!" push to all devices (fires once) |
| Battery < 25% (probes) or < 20% (base) | 🔋 Battery low push |
| Meat type set back to None | Alert flag resets, ready for next cook |

### Helpers created

| Entity ID | Type | Purpose |
|-----------|------|---------|
| `input_select.probe_1_meat_type` | Dropdown | Triggers target temp automation |
| `input_select.probe_2_meat_type` | Dropdown | Triggers target temp automation |
| `input_number.probe_1_target_temp` | Number | Target temp for probe 1 |
| `input_number.probe_2_target_temp` | Number | Target temp for probe 2 |
| `input_boolean.probe_1_alert_sent` | Toggle | Prevents duplicate done alerts |
| `input_boolean.probe_2_alert_sent` | Toggle | Prevents duplicate done alerts |

### Automations created

| Alias | Trigger | Action |
|-------|---------|--------|
| Traeger Probe 1 Set Target | Probe 1 meat type changes | Sets target temp number |
| Traeger Probe 2 Set Target | Probe 2 meat type changes | Sets target temp number |
| Traeger Probe 1 Almost Done | Probe 1 within 10°F of target | Push notification |
| Traeger Probe 2 Almost Done | Probe 2 within 10°F of target | Push notification |
| Traeger Probe 1 Target Reached | Probe 1 hits target | Push notification (once) |
| Traeger Probe 2 Target Reached | Probe 2 hits target | Push notification (once) |
| Traeger Reset Probe 1 Alert | Probe 1 set to None | Resets alert flag |
| Traeger Reset Probe 2 Alert | Probe 2 set to None | Resets alert flag |
| Traeger Battery Low | Any battery drops below threshold | Push notification |

---

## Uninstall

Remove the integration from **Settings → Devices & Services** — all helpers, automations, and www files are cleaned up automatically.

---

## Changelog

### v1.3.0
- Full mobile-first redesign — compact rows, tap to expand details inline
- Device status bar redesigned as 3-column wrapping grid (no side scrolling)
- Category chips wrap naturally across multiple rows, nothing hidden
- Custom food builder collapsed by default, tap to expand
- Reset openIdx on search and category change for clean UX

### v1.2.0
- Added live device status bar (connection, charging, battery for all 3 units)
- Minimalist layout with tap-to-expand food detail panels
- Custom food builder with localStorage persistence and delete support

### v1.1.1
- Fixed WebSocket connection for HTTPS/DuckDNS (correctly uses `wss://` on port 443)
- Added console debug logging for WebSocket URL

### v1.1.0
- Token prompt saves automatically on entry, never asks again on same browser
- Added `HA_TOKEN` constant for hardcoded permanent token on all devices

### v1.0.8 — v1.0.9
- Fixed JavaScript syntax error in P1/P2 button onclick caused by special characters in food names (°, –)
- Replaced JSON string serialization with index-based `_itemRegistry` lookup

### v1.0.7
- Fixed `www_install.py` — HTML now bundled inside `custom_components/traeger_cook_guide/` since HACS only downloads that folder
- Fixed `persistent_notification` import for current HA versions
- Fixed component readiness — now waits for `homeassistant_started` event before creating helpers/automations
- Added polling loop to confirm `storage_collection` is available before writing

### v1.0.5 — v1.0.6
- Fixed manifest key ordering for hassfest compliance (`domain`, `name`, then alphabetical)
- Added `CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)` — required by hassfest
- Renamed `custom_component` → `custom_components` (critical folder name fix)
- Added `brand/icon.png` — required by HACS validator
- Removed `validate-hacs` GitHub Action (only needed for public store submission)
- All entity IDs updated to `bt_proxy_` prefix to match ESPHome BT proxy naming

### v1.0.0 — v1.0.4
- Initial HACS integration release
- Interactive cook guide with 60+ foods
- One-click probe assignment via HA WebSocket
- 6 helpers and 9 automations auto-created on setup
- Push notifications via `notify.notify`

---

## Repository structure

```
traeger-cook-guide/
├── hacs.json
├── README.md
├── LICENSE
├── brand/
│   └── icon.png
├── www/
│   └── traeger_cook_guide.html         ← reference copy (not used by HACS)
└── custom_components/
    └── traeger_cook_guide/
        ├── __init__.py                 ← orchestrates setup/teardown
        ├── manifest.json               ← version, domain, codeowners
        ├── config_flow.py              ← one-click install UI (no fields)
        ├── const.py                    ← all entity IDs and constants
        ├── helpers.py                  ← creates 6 HA helpers via StorageCollection
        ├── automations.py              ← creates 9 HA automations via StorageCollection
        ├── www_install.py              ← copies HTML to /config/www/traeger_cook_guide/
        ├── strings.json                ← UI strings for config flow
        └── traeger_cook_guide.html     ← interactive cook guide (bundled here for HACS)
```

---

## Support

Open an issue at [github.com/night-owl-018/traeger-cook-guide/issues](https://github.com/night-owl-018/traeger-cook-guide/issues)
