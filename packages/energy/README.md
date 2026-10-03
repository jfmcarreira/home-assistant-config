# Energy measurements and estimates

This folder derives energy-related values; inverter control workflows live in
`automations.yaml`, and the Modbus device definition is under
[`esphome/phosphorus/`](../../esphome/phosphorus/README.md).

| File | Role |
| --- | --- |
| `battery.yaml` | Charging-time display and remaining charging energy using a configured 11.8 kWh capacity assumption. Negative battery power means charging in these calculations. |
| `bhpzem_meter.yaml` | Meter-derived values for the BHPZEM installation. |
| `electricity_price.yaml` | Electricity-pricing entities used alongside consumption. |
| `light_power.yaml` | Attributed lighting power. |
| `remaining_power.yaml` | House consumption minus tracked `device_power_*` values and total lighting power. |

The remaining-power value is an accounting residual, not an independently measured
circuit. Its device list is selected by naming prefix, so adding another
`device_power_*` sensor changes the calculation.

Battery/forecast values feed both solar HVAC eligibility and inverter routines.
Root workflows manage export, charge current, time-of-use SOC targets and low-battery
HVAC shutdown. Water heating also has direct-switch PV support, distinct from its
normal thermostat and solar-thermal panel heating.
