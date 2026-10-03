# Manual utility-meter readings

`meters.yaml` provides manual full/peak/off-peak electricity readings and a manual
water-meter reading. A template sums the electricity register values.

Changes are queued for insertion into the external `meters_tracking` table using
the matching register column. The stored timestamp is rounded to the current
hour, not the exact edit time. Up to 20 runs can queue per write automation.

These manual billing readings are distinct from device power accounting in
[`energy/`](../energy/README.md) and pulse-based flow/volume measurements in
[`water/`](../water/README.md).
