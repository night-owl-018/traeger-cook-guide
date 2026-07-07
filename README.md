# 🔥 Traeger Cook Guide for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/night-owl-018/traeger-cook-guide/releases)
[![HA](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-brightgreen.svg)](https://www.home-assistant.io)

A zero-touch HACS integration that installs a full interactive Traeger smoker cook guide into your Home Assistant. Browse 60+ foods with smoker temps, cook times, and internal targets — tap any food to assign it to one of your **four Govee H5198 probes**. Pick any probe to watch the grill as a **pit probe**, and HA handles the rest: sets target temps, warns at 10°F out, fires when it's ready to pull, and alerts if the pit runs hot or the fire drops.

> **v2.0 — now built for the Govee H5198 4-probe thermometer.** This is a breaking change from the 1.x HOPEPOP builds: the entity IDs, probe count, and helpers are all different. See [Migrating from 1.x](#migrating-from-1x) below.

---

## Features

- 🍖 **60+ foods** across 8 categories — Beef, Pork, Poultry, Seafood, Lamb, Vegetables, Sides, Desserts
- 🌡️ **Four probes** — assign a different food to each of P1–P4, or leave any unused
- 🔥 **Selectable pit probe** — promote any probe to watch the grill; it shows live pit temp, holds a target, and alarms on flare-ups or a dying fire
- 📱 **Mobile-first design** — compact rows, tap to expand details, 2×2 probe grid, no side scrolling
- 📊 **Live progress bars** — real-time temp with green → amber → red fill toward each target
- 🔔 **Push notifications** — 10°F warning, "ready to pull," and pit high/low drift alerts, broadcast to all HA users/devices via `notify.notify`
- 🔌 **Derived connection status** — a live "Thermometer connected" strip inferred from probe availability (Govee reports no connection entity)
- ✍️ **Custom food builder** — add your own cuts with target temp, cook time, and notes; persists across refreshes via localStorage
- 🌙 **Dark mode** — automatic, follows system preference
- 🔒 **Token persistence** — enter your HA token once per browser, never asked again

---

## What gets installed automatically

When you click **Submit** in the integration setup:

| What | Details |
|------|---------|
| 📄 Cook guide HTML | Copied to `/config/www/traeger_cook_guide/` |
| 🔧 14 helpers | 4 meat-type dropdowns, 4 target-temp numbers, 4 alert toggles, 1 pit-probe selector, 1 pit-target number |
| ⚡ 18 automations | Per-probe set target / almost done / target reached / reset (×4), plus pit high-drift and low-drift |
| 📋 Notification | Dashboard card YAML to paste (1 manual step) |

---

## Requirements

- Home Assistant 2024.1+
- HACS installed
- A **Govee H5198** thermometer added to Home Assistant, producing these entity IDs:

**Live probe temperatures**

| Entity ID | What it is |
|-----------|-----------|
| `sensor.govee_meat_thermometer_temperature_probe_1` | Probe 1 live temperature |
| `sensor.govee_meat_thermometer_temperature_probe_2` | Probe 2 live temperature |
| `sensor.govee_meat_thermometer_temperature_probe_3` | Probe 3 live temperature |
| `sensor.govee_meat_thermometer_temperature_probe_4` | Probe 4 live temperature |

**High / low temperature alarms** (device thresholds, used as a safety backstop)

| Entity ID |
|-----------|
| `sensor.govee_meat_thermometer_temperature_alarm_probe_1` … `_probe_4` |
| `sensor.govee_meat_thermometer_low_temperature_alarm_probe_1` … `_probe_4` |

> **No battery, connection, or charging sensors are used** — the Govee integration doesn't expose them. Connection is derived instead: a probe counts as "live" when its temperature reads a real number rather than `unavailable`, and the header strip turns green when any probe is live.
>
> If your Govee integration names these entities differently, update the `ENT` map at the top of the `<script>` in `traeger_cook_guide.html` and the entity constants in `const.py` — nothing else needs to change.

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

A persistent notification appears after setup with the YAML. Add it as a **Manual** card on your dashboard:

```yaml
type: iframe
url: /local/traeger_cook_guide/traeger_cook_guide.html
aspect_ratio: "100%"
title: Traeger Cook Guide
```

> **HTTPS users (DuckDNS, Nabu Casa, etc.):** if the iframe shows blank, add this under the `http:` section of `configuration.yaml` and restart HA:
> ```yaml
> http:
>   use_x_frame_options: false
> ```
> This is safe for a single-user home setup.

### Step 4 — Authenticate the cook guide

1. **Profile → Long-Lived Access Tokens → Create Token** → name it `Traeger Cook Guide`
2. Open the cook guide — it prompts for the token on first load
3. The token is saved to `localStorage`, never asked again on that browser/device

To skip the prompt on **all** devices, paste your token into the `HA_TOKEN` constant near the top of the JavaScript in `traeger_cook_guide.html`.

---

## How it works

### Assigning food to a probe

Tap **P1–P4** on any food row. The guide writes three values to HA over the WebSocket API: the meat type (`input_select.probe_N_meat_type`, which triggers the target-temp automation), the target temp directly as a backup (`input_number.probe_N_target_temp`), and resets the alert flag. Each probe tracks its own food, elapsed time, and progress independently.

### The pit probe

Tap **Off / P1 / P2 / P3 / P4** in the grill card to choose which probe watches the pit. That probe drops out of the food pool (its food-row button becomes a flame lock), shows the live grill temperature up top, and holds a target (default 225°F, adjustable). Assigning a food to another probe auto-nudges the pit target to that recipe's smoker temp. The choice and target persist locally and sync from HA on load.

| Event | What fires |
|-------|-----------|
| Food probe within 10°F of target | ⚠️ "Almost Done" push |
| Food probe reaches target | 🍖 "Ready to pull!" push (once) |
| Pit rises above target + 25°F | 🔥 "Running hot" alert (flare-up) |
| Pit falls below target − 25°F | ❄️ "Fire dropping" alert |
| Meat type set back to None | Alert flag resets, ready for next cook |

---

## Migrating from 1.x

1.x targeted a 2-probe HOPEPOP thermometer over an ESPHome BT proxy. v2.0 targets the 4-probe Govee H5198. If you're upgrading:

- Remove the old integration first (this cleans up the 1.x helpers and automations), then install v2.0 fresh so the new 14-helper set is created.
- The `sensor.bt_proxy_hopepop_*` entities are no longer used — the guide now reads `sensor.govee_meat_thermometer_*`.
- Battery and charging cards are gone; the connection indicator is now derived from probe availability.

---

## Uninstall

Remove the integration from **Settings → Devices & Services** — all helpers, automations, and www files are cleaned up automatically.

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
        ├── const.py                    ← Govee entity IDs + helper/automation IDs
        ├── helpers.py                  ← creates the 14 HA helpers
        ├── automations.py              ← creates the 18 HA automations
        ├── www_install.py              ← copies HTML to /config/www/traeger_cook_guide/
        ├── strings.json                ← UI strings for config flow
        └── traeger_cook_guide.html     ← interactive cook guide (bundled here for HACS)
```

---

## Support

Open an issue at [github.com/night-owl-018/traeger-cook-guide/issues](https://github.com/night-owl-018/traeger-cook-guide/issues)
