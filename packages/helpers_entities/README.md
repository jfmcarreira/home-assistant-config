# Time and seasonal inputs

`hot_months.yaml` marks April through September as hot months. The template HVAC
switch facades use this calendar rule to choose cooling versus heating; it is
not a measured-temperature decision and differs from the `sensor.season` checks
used by scheduled HVAC blueprints.

`tod_morning_before_work.yaml` is on from 07:30 through 10:00 on workdays.
These entities are reusable inputs rather than standalone device-control routines.
