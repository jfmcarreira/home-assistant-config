# Derived sensors

These packages normalize installation-specific signals for workflows and cards.
They generally do not actuate devices.

| Location | Consumers and interpretation |
| --- | --- |
| `house_mode/` | Display mapping for the AppDaemon selector, Night/Sleep flag, guest/cleaning presence and combined household occupancy. See [HouseMode](../../appdaemon/README.md). |
| `persons/` | Joao/Bianca home-state signals and active-at-home MacBook state used for arrivals and notifications. |
| `lights/` | Lighting state summaries for living floor, bedroom floor and exterior cards. |
| `bathroom/` | Filtered bathroom humidity for portable-device climate control. |
| `stock/` | Litter/filter stock representations used with replacement tasks and Grocy. |
| `average_temperature*.yaml`, `average_humidity_exterior.yaml` | Room statistics and filtered outdoor readings used by HVAC, shutters and dehumidifier targets. |
| `cctv_smart_detection.yaml`, `gate.yaml` | Derived camera/gate state used by exterior routines. |
| `date_time.yaml`, `temperature_trend.yaml` | Date/time displays and temperature trend state. |

`room_presence.yaml` currently contains only commented-out MQTT room-presence
examples; it does not create active trackers. Actual room trackers, if present,
come from other installation configuration. Household occupancy is an OR of
resident and guest state, not an OR of motion sensors.

Entity naming varies by source and age (`temperature_<room>`, `<room>_state`,
floor summaries). Consult consumers before interpreting a display label as a
physical-room ID; upstairs `hall` and ground-floor `hallway` are distinct.
