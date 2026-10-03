# Tablet home-page reset

These two automations return the Fully Kiosk tablets to their configured dashboard
URLs after screen-off, house Off/Sleep, household absence or sustained clear motion.
They compare the current page first to avoid reloading an already-correct page.

- Hall reset watches stair motion and targets the Fire tablet.
- Living-room reset watches the listed living-room, hallway, kitchen and stair
  sensors and targets the Lenovo tablet. Each sensor can independently trigger it.

The URL values are secret references. Screen brightness, motion detection and
timeouts are controlled separately by root automations; page content is in
[`dashboards/`](../../dashboards/README.md).
