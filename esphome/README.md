# Device firmware

Top-level YAML/YML files are device entry points. They compose shared ESPHome
packages with per-device names, pins, relay assignments, timings and calibration.
They are separate from Home Assistant's `packages/` include system.

| Entry-point family | Hardware role |
| --- | --- |
| `bhonofre_cover_*` | Room shutter controllers with local buttons and extra button actions. |
| `shelly*` | Room/exterior relay, lighting and bathroom controls across several hardware generations. |
| `sonoff*` | Gate lighting, RF bridge, switching and floor power measurement. |
| `nodemcu_gate.yml` | Gate controller. |
| `d1-mini-water-meter.yml`, `nodemcu-water-kitchen.yml` | Pulse-based water measurement. |
| `bhpzemmain.yml` | Electrical metering node. |
| `phosphorus.yml` | Combined Deye inverter, cooling and solar-thermal/water measurement node. |
| `m5stack-atom-echo.yml` | Voice hardware entry point. |

- [Shared firmware packages](packages/README.md) explain device-local behavior.
- [Phosphorus composition](phosphorus/README.md) explains the energy/water node.
- `components/sc_cover/` contains a local cover component; its existing README
  documents its own implementation.

Home Assistant entity IDs can differ from firmware names because of registry
renaming. Root workflows consume both native entities and ESPHome services/events,
including `esphome.button_pressed`. Firmware-local relay control is distinct from
the HA automation responding to an auxiliary button event.

Secrets and build/cache output are not documentation inputs. Changing a firmware
source requires its own ESPHome validation/build/upload workflow; editing the
Home Assistant copy alone does not update a device.
