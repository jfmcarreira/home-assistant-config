# Device-specific support

`assistant_speakers.yaml` provides assistant-speaker support, while the root
volume automation adjusts only idle/off players according to day/evening/night
volume helpers. Doorbell announcements and media actions are root scripts.

`baby_monitor.yaml` provides monitor-related state used by the crying/movement
alerts. Each root alert adds its own resident, room-light, shutter, time and
house-mode conditions; a monitor signal alone does not guarantee notification.

`roborock.yaml` exposes room-selection helpers and a Valetudo segment-cleaning
script. Its current payload includes only the upstairs room selections and
requires at least one of them selected. Ground-floor helpers are defined but
are not added to the segment payload; all selections are cleared after publishing.
Segment IDs are map-specific, not Home Assistant area IDs.
