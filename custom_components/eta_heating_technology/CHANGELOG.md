# ETA Heating Technology – Code Review & Changes

**Date:** 2026-02-21  
**Base Version:** 0.3.0  
**Current Version:** 0.5.0

---

## v0.5.0 – Robustness, Performance & HA Best Practices

### Crash Prevention (`api.py`)
- **`ZeroDivisionError`**: `scaled_value` now guards against `scaleFactor="0"` and falls back to `strValue`
- **`ValueError`**: Non-numeric XML values are caught with try/except instead of crashing the coordinator
- `scaled_value` now returns `float` for numeric (unit-bearing) values instead of `str`

### Sensor Accuracy (`sensor.py`)
- **Numeric sensors return `float`** — enables proper HA long-term statistics, history graphs, and energy dashboard
- **`kWh` sensors** use `SensorStateClass.TOTAL_INCREASING` (was `MEASUREMENT`) — required for energy dashboard
- **`kg` sensors** use `SensorStateClass.TOTAL` for cumulative weight tracking

### Performance (`coordinator.py`)
- **`asyncio.gather()`** fetches all entity values concurrently instead of sequentially — 20 entities now finish in ~1 request time instead of ~20x
- Individual fetch failures are logged as warnings instead of crashing the entire update cycle
- Return type annotated as `dict[str, Value]`

### Data Integrity (`config_flow.py`)
- Pydantic `Object` instances are now **serialized to dicts** (`obj.as_dict()`) before storing in `config_entry.data` — ensures reliable JSON persistence across HA restarts

### Switch Improvements (`switch.py`)
- **Optimistic state updates**: UI reflects the new state immediately after toggle, before the coordinator refresh confirms it
- Extracted `_async_set_state()` helper — eliminates duplicated `turn_on`/`turn_off` logic
- Removed redundant `self.coordinator = coordinator` assignment (already set by parent class)

### Logging
- `_LOGGER.error` for `None` values during startup/partial failures → `_LOGGER.warning` (sensor.py, switch.py)

### Manifest
- Added `"homeassistant": "2024.4.0"` minimum version requirement
- Version bumped to `0.5.0`

---

## v0.4.0 – String Sensor Detection & strValue Fallback

### String Sensor Detection

| Change | Files | Impact |
|--------|-------|--------|
| Reordered `determine_sensor_type`: binary check before string check | `utils.py` | Correct priority — binary values (1802/1803) are no longer misclassified |
| Added `strValue` fallback for unknown state codes | `utils.py` | Unitless values with a non-empty `strValue` from the API are now recognized as `STRING_SENSOR` even when the numeric code isn't in the hardcoded mapping |
| `EtaStringSensor.native_value` falls back to `value.str_value` | `sensor.py` | Instead of returning `None` for unmapped codes, uses the text the ETA API already provides (e.g. "Heizen", "Bereit", "Störung") |

**Why:** The ETA system uses different code ranges per fub (e.g. 2000-range for HK/Puffer, 4000-range for Kessel). The old code only mapped 2000-range codes, so entities like *Kessel Betriebszustand* were silently skipped. Now **all** state entities work out of the box.

---

## v0.3.0 → v0.4.0 – Initial Code Review & Fixes

### Critical Bug Fixes

#### 1. Broken control flow in switch setup (`switch.py`)
The entity setup loop had unreachable code — the `sensor_type is None` error check could never execute because the preceding `sensor_type is not BINARY_SENSOR` check already triggered `continue` for `None`. Switches were silently not added.  
**Fix:** Clean `if` block with direct `append`.

#### 2. Potential `UnboundLocalError` in sensor setup (`sensor.py`)
Separate `if` statements (instead of `if/elif/else`) meant the variable `e` could be unassigned when appending, causing a crash for unexpected sensor types.  
**Fix:** Restructured to proper `if/elif/else` chain with inline `append`.

#### 3. `scaled_value` returned empty string (`api.py`)
When a value had no unit (binary/string sensors), `scaled_value` returned `""` instead of the actual value.  
**Fix:** Returns `self.str_value` for unitless values.

#### 4. Inconsistent name sanitization (`api.py`)
`Fub.model_post_init` used raw `self.name` for `full_name` but `self.sanitized_name` for `namespace`, causing naming mismatches between top-level and nested objects.  
**Fix:** Uses `self.sanitized_name` consistently.

---

## Duplicate Device Fix

### Problem
Every time a new config entry was added (e.g. to monitor additional entities), a new device was created in Home Assistant. This resulted in multiple "ETA Heating" devices for the same physical heater.

### Root Cause
- Device identifier used `config_entry.entry_id` (unique per entry) instead of a stable key.
- No `unique_id` was set on the config entry, so HA allowed unlimited entries for the same device.

### Changes

| File | Change |
|------|--------|
| `__init__.py` | Device identifier changed to `(DOMAIN, "host:port")` |
| `entity.py` | Entity `DeviceInfo.identifiers` changed to match `"host:port"` |
| `config_flow.py` | `unique_id` set to `"host:port"` with `_abort_if_unique_id_configured()` |

---

## Options Flow (New Feature)

Added an **Options Flow** so entities can be added or removed from an existing config entry — no need to create a new entry.

| File | Change |
|------|--------|
| `config_flow.py` | New `EtaOptionsFlowHandler` class with `async_step_select_entities` |
| `config_flow.py` | `async_get_options_flow()` registered on `EtaFlowHandler` |
| `translations/en.json` | Added `options` section with step/error/abort translations |

**Usage:** Click the gear icon (⚙️) on the existing config entry → select/deselect entities → save.

---

## Performance & Robustness

| Change | Files | Impact |
|--------|-------|--------|
| Cached `Object.model_validate()` in coordinator | `coordinator.py` | No more re-parsing config data every 60s update cycle |
| Deduplicated API calls on platform setup | `sensor.py`, `switch.py` | Sensor & switch platforms reuse coordinator data instead of each calling the API for all objects |
| `Value.unit` changed from `Literal` to `str` | `api.py` | Integration no longer crashes if ETA returns an unexpected unit |
| `ETA_SENSOR_UNITS[unit]` → `.get(unit)` | `sensor.py` | Graceful handling of unknown units (returns `None` device class) |
| `Eta.as_dict()` missing `success` field | `api.py` | Complete serialization |

---

## Sensor Improvements

| Change | Files | Impact |
|--------|-------|--------|
| Added `SensorStateClass.MEASUREMENT` | `sensor.py` | Numeric sensors now appear in HA **long-term statistics** and the **Energy dashboard** |
| Removed unused `api_client`/`url` from sensor entities | `sensor.py` | Cleaner constructors — only switches need direct API access |

---

## Code Quality Improvements

| Change | Files |
|--------|-------|
| Absolute imports → relative imports | `api.py`, `coordinator.py`, `sensor.py`, `switch.py`, `utils.py` |
| Replaced deprecated `async_timeout` with `asyncio.timeout` | `api.py` |
| Excessive `INFO` logging → `DEBUG` | `sensor.py`, `switch.py`, `coordinator.py`, `__init__.py` |
| Removed unused `ValueNoneError` class | `sensor.py`, `switch.py` |
| Removed unused `EtaBinarySensor` class | `sensor.py` |
| Removed unused `integration` field from `EtaData` | `data.py`, `__init__.py` |
| Removed unused imports (`Object`, `CHOSEN_ENTITIES`, etc.) | `sensor.py`, `switch.py` |
| Fixed `async_reload_entry` to use `hass.config_entries.async_reload()` | `__init__.py` |
| Fixed switch module docstring ("Sensor" → "Switch") | `switch.py` |
| Fixed `EtaStringSensor` class docstring | `sensor.py` |
| `build_endpoint_url` uses f-string instead of concatenation | `api.py` |
| Fixed `ISSUE_URL` mismatch (const.py vs manifest.json) | `const.py` |

---

## Translations

| Change | Files |
|--------|-------|
| Fixed grammar in English translation | `translations/en.json` |
| Added `options` flow translations (EN) | `translations/en.json` |
| Added `already_configured` abort message (EN) | `translations/en.json` |
| Added complete German translations | `translations/de.json` (new) |

---

## Branding

Icon and logo files for the integration banner were prepared using the official ETA Heiztechnik icon from eta.co.at.

| File | Size | Purpose |
|------|------|---------|
| `icon.png` | 256×256 | Local integration icon |
| `icon@2x.png` | 180×180 | Local retina icon |
| `logo.png` | 256×256 | Local integration logo |

A ready-to-submit PR structure for the [home-assistant/brands](https://github.com/home-assistant/brands) repository is prepared in `brands_pr/`. See `brands_pr/README.md` for step-by-step submission instructions.
