# Climate switch facades

These fragments are included as template switches. They expose simple on/off
controls for climate devices without replacing the underlying climate entities.

Room AC switches choose heating or cooling from `binary_sensor.hot_months`
(April–September), then apply their configured setpoint/fan actions. For example,
the living-room facade requests 24 C cooling or 22 C heating with auto fan.
Its state is on when the climate entity is neither off nor unavailable.

Other room files have their own settings; `air_switch.yaml` is a separate facade.
The switches do not apply all of the scheduled-HVAC blueprint's presence,
window, solar or bypass checks. A physical button or dashboard invoking one is
not equivalent to triggering a scheduled automation.
