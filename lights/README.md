# Template-light facades

Each YAML fragment defines one template light and is loaded under `template.light`
with `!include_dir_list`. These are control facades, not necessarily ordinary
light groups: the lights used to compute state can differ from the turn-on target,
and turn-off can target a whole area.

For example, `bathroom_rc.yaml` reports on when either the ceiling or LED is on,
turns on only the LED, and turns off the entire bathroom area. Read all three
parts before assuming a room-light command addresses every lamp identically.

Room files coexist with hall/hallway/living-room/exterior groups and seasonal
Christmas facades. The motion controller uses these targets and blockers; separate
root automations apply lighting scenes after selected physical lights turn on.
Bright/manual lighting and low-level presence lighting therefore have different
entry points.

These template entities do not support an arbitrary `description` property.
Automation/script UI descriptions and this README document their contracts.
