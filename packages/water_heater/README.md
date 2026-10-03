# Hot-water control

Three control paths share the hot-water system:

| Path | Entry points |
| --- | --- |
| Electric thermostat | `water_heater.yaml`, exposed as `climate.water_heater`, operating `switch.water_heater` from tank-top temperature. |
| Solar-thermal heating detection | `water_heater_pump_state.yaml` and `water_heater_solar_panel_heating.yaml`. |
| Direct photovoltaic support | Root automations directly operate the heater switch only while the thermostat is off. |

The generic thermostat allows targets from 38 to 55 C, uses zero cold tolerance,
1 C hot tolerance and a five-minute minimum cycle. Its eco temperature is 40 C.
Morning/afternoon scheduling and preset changes are in `automations.yaml`.

`binary_sensor.water_heater_panel_heating` requires sun elevation above 10 degrees
and pump activity. It has a 30-minute off delay, so downstream checks for ten,
15, 30 or 60 minutes of inactive panel heating add to that delayed signal.

Direct PV support is not the thermostat setpoint routine: it uses the separate
solar-excess temperature helper, battery/PV checks and a minimum ten-minute
switch interval. The two paths' ownership checks keep those root actions from
deliberately overriding an enabled thermostat.

Device-side solar-panel and pump-related measurements are composed into the
[Phosphorus firmware](../../esphome/phosphorus/README.md). Sensor names and
configured paths describe the known topology; tank size and physical plumbing
are not specified in this repository.
