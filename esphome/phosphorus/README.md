# Phosphorus energy and water node

`../phosphorus.yml` is the ESP32 entry point. It composes:

- `deye_hybrid_1p.yaml`: Deye single-phase hybrid inverter Modbus entities.
- `deye_fan_controller.yaml`: inverter cooling control.
- `water_heater_solar_panel.yaml`: solar-thermal water-heater measurements/control.

The entry point also defines a one-wire temperature sensor and washing-machine
water-flow/volume pulse counting. Its documented ZJ-B5 calibration is approximately
396 pulses per litre, with multiplier `0.002525`.

Inverter entities feed HA battery calculations, PV-assisted HVAC, export and
time-of-use routines. Solar-thermal signals feed hot-water heating detection;
they are distinct from electrical PV production. The related HA models are in
[`packages/energy/`](../../packages/energy/README.md),
[`packages/water/`](../../packages/water/README.md) and
[`packages/water_heater/`](../../packages/water_heater/README.md).
