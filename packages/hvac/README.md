# Climate support

The root workflows and [`HVAC blueprints`](../../blueprints/README.md) handle
schedules, solar support and room routines. This package models portable devices
and supplies low-level resets.

- `portable_heater.yaml` exposes a generic thermostat over the heater switch.
  `portable_heater_temperature.yaml` chooses the measured temperature from the
  selected location; moving the heater requires updating that location helper.
- `dehumidifier.yaml` exposes a generic hygrostat over the dehumidifier switch.
  `dehumidifier_humidity.yaml` chooses humidity by the location helper.
- `automations/reset_controls.yaml` restores setpoints, fan modes and unit-specific
  swing settings after living-room, master-bedroom and Ricardo AC shut down.

The portable heater is seasonal and may legitimately be unavailable in warmer
months. AC drying routines use each air conditioner's dry mode and are separate
from the portable dehumidifier.

## Shared scheduled-HVAC rules

`hvac_time_turn_on.yaml` requires the units off, HVAC bypass and extended-away
mode off, selected season/day/time, the supplied window sensor clear and the
whole-house window sensor clear. Heating compares both room and outdoor
temperature to the instance threshold; cooling compares room temperature.
Both also compare against the house target band and apply a 12-hour run interval.

The schedule end is an eligibility boundary, not a shutdown action. Shutdown
automations are separate. An instance can offset its setpoint after one hour.

Solar HVAC is split between an eligibility automation and an action script.
The former checks PV, household load, battery, forecast, absence, cleaning state
and windows. The latter selects heat/cool and waits for stop transitions without
an overall timeout. Directly invoking that script bypasses the eligibility layer.

The extended-away overheating blueprint is separate: it cools above 26 C to a
25 C target, with PV/load gates and a four-hour maximum wait before shutdown.
Simple dashboard switch controls live in [`switches_hvac/`](../../switches_hvac/README.md).
