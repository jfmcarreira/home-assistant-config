# HouseMode app

`apps.yaml` enables `HouseModeApp` from `HouseMode.py`. This app is running and
manages `input_select.house_mode`. `CoverControls.py` is not registered in the
current app configuration and is scheduled for removal.

## Modes and consumers

| Selector value | Display sensor value | Intended role |
| --- | --- | --- |
| `On` | `Ligada` | Normal daytime automatic lighting. |
| `Evening` | `Amanhecer/Anoitecer` | Dawn/evening lighting policy. |
| `Night` | `Noite` | Nighttime lighting levels and restricted room behavior while awake. |
| `Sleep` | `Dormir` | Residents are in bed; most indoor motion lighting is blocked. |
| `Off` | `Desligada` | House empty; automatic indoor lighting must not respond to cats. |

`packages/sensors/house_mode/house_mode.yaml` supplies the display mapping.
`binary_sensor.night_mode` is on in both Night and Sleep and selects day/night
lighting scenes. Mode changes also drive tablets and Frigate profiles.

## How the app decides

- Presence is based on Joao and Bianca's **person entities**. If neither is home,
  the next evaluation selects Off. This differs from `notify_home`, which also
  includes guest/cleaning presence.
- Preferred Evening windows are 06:30–07:30 and 19:30–21:30. From 21:30–06:30,
  guests keep the preferred mode Evening; otherwise it is Night. Other times
  prefer On.
- Sleep can be selected from Evening or Night after inactivity during 00:00–07:00,
  when tracked lights/devices are off and the app's door-delay flag allows it.
- Inactivity waits are two minutes during 01:00–07:00 and 36 minutes otherwise.
  Tracked TV and active-at-home MacBook state also count as active devices.
- Sustained light-on, resident-presence and bedroom-shutter-open events can move
  Sleep back to the preferred mode. Motion alone does not wake Sleep.
- Daily reevaluations run at the explicit times listed in `initialize()`; a mode
  change also schedules a 20-minute transition reevaluation.

These are the implemented state-machine rules, not a claim that every preferred
time immediately forces a transition. Each current mode handles events differently.

## Manual control and cat motion

Root good-night/departure/night routines and `scripts/helpers/house_mode.yaml`
also write the selector. The app listens to those changes and updates its internal
mode. Motion-light blueprint instances separately enforce presence, a global
motion-light switch, room-mode eligibility and optional Sleep/Guest blocking.
Outdoor instances may allow Sleep while still requiring household presence.

The tracked entity lists and door-delay implementation are in `HouseMode.py`;
they must be consulted when explaining a transition. This documentation does not
equate raw motion with a person being awake.
