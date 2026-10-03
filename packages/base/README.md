# Shared installation services

| File | Responsibility |
| --- | --- |
| `recorder.yaml`, `logbook.yaml`, `influxdb.yaml` | History retention/filtering and time-series export configuration. |
| `external_db.yaml` | Task/meter database wiring and the database-insertion shell command used by task blueprints and utility workflows. |
| `install_deps.yaml` | Exposes installation-specific dependency setup commands. |
| `notifications.yaml` | Mobile notification grouping used by shared workflows. |
| `do_not_disturb.yaml` | Combines a manual helper, schedule and both phones' do-not-disturb states. |
| `browser_mod.yaml` | Browser Mod support for tablet popup actions. |
| `rf_demux.yaml` | Receives Tasmota RF messages and dispatches them to the Python decoder. |
| `zha.yaml` | Retained ZHA configuration; the current setup uses Zigbee2MQTT. |

Do-not-disturb treats a phone state other than `off` as blocking, including
unknown/unavailable states. Callers decide whether to honor this signal: task
reminders and audible doorbell actions use it, while security/mobile snapshot
paths can have different conditions.

RF decoding is a cross-layer path from the configured MQTT bridge topic to
`python_script.rf_bridge_demux`, then to per-device `binary_rf_sensors/*` topics.
Database credentials and connection values are not documented here.
