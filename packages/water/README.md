# Water measurement

`water_total.yaml` sums flow and cumulative volume for washing machine,
dishwasher, kitchen-sink hot/cold, garden and cleaning branches. Flow uses L/min;
volume uses L with `total_increasing` state class.

Both totals require every listed source to have a value. An unavailable branch
makes the total unavailable rather than silently treating that branch as zero.
The total is the sum of these monitored branches, not proof of a complete
whole-property meter.

`portable_water_meter.yaml` attributes one portable meter to Garden or Cleaning
using a destination selector. Only the selected branch receives current flow
and positive volume increments; the other branch retains its accumulated volume.
If the device total resets, the new value becomes the increment rather than a
negative subtraction. Flow falls back to zero when the source is not numeric.

Physical pulse counting/calibration lives in ESPHome; manual billing readings
are separate in [`utilities/`](../utilities/README.md).
