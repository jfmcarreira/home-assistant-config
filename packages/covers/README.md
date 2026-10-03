# Shutter control

The main shutter policies are in `automations.yaml`: sunrise/sunset, heat,
rain and extended-away behavior. This folder supplies their common execution
layer and per-room choices.

## Dispatch and policy helpers

`cover_group_action.yaml` accepts room suffixes such as `kitchen`, an action such
as `cover.close_cover` or `script.cover_close_when_raining`, and a helper suffix
such as `close_with_heat`.

Each worker checks `input_boolean.cover_control_<policy>_<room>` before acting.
Script actions receive `action_cover`; direct services target `cover.<room>`.
Workers run independently, up to 20 at once, and the dispatcher does not wait for
them to finish.

| Helper files | Purpose |
| --- | --- |
| `cover_helpers_group.yaml` | Membership of the aggregate floor controls. |
| `cover_helpers_sunrise_sunset.yaml` | Per-room sunrise/sunset participation. |
| `cover_helpers_close_heat.yaml`, `cover_helpers_close_rain.yaml` | Per-room heat/rain participation. |
| `cover_helpers_positions.yaml` | Room-specific positions, including rainy positions. |
| `cover_switch.yaml` | Derived cover-control availability. |

`first_floor.yaml` represents the ground floor; `second_floor.yaml` represents
the upstairs bedrooms and stairs. Their displayed positions average only the
selected rooms. `cover.bathroom` belongs to the ground-floor bathroom; see the
[room map](../../docs/house-layout.md).

## Last-action reason

Group control maps sunrise to `Sunrise`, sunset to `Sunset`, rain to `Chuva`,
and heat to `Sol`; other group actions use `Grupo`. Ten seconds after issuing
an action, the worker records the reason. Stairs use an `input_select`; the
other shutters use ESPHome `select` entities.

The root last-action automation marks shutter changes `Manualmente`, including
attribute changes. The delayed worker write restores a group reason afterward.
The heat-reopening helper checks for `Sol` so it does not deliberately reopen
a shutter closed manually or for another reason.

## Action argument convention

The helpers in `actions.yaml` construct `cover.{{ action_cover }}`; callers must
pass a room suffix, not `cover.kitchen`, despite the existing entity selector and
examples. Rain adjustment first closes a shutter that is above its rainy position,
waits at most one minute for closed state, and then requests its rainy position.
The position request still runs after that timeout.

Physical button handling, opening-position calibration and device-local fallback
are in [`esphome/packages/`](../../esphome/packages/README.md). Extended-away
sunrise/sunset workflows use direct label/floor targets instead of this dispatcher.
