# Reusable Home Assistant logic

Blueprint instances in the root workflows supply room-specific targets and inputs.
These are Home Assistant blueprints, not ESPHome packages. The same relative
filename can occur under `automation/` and `script/` with a different role.

| Local family | Shared behavior |
| --- | --- |
| `automation/lights/` | Motion-owned lighting, scene selection and selected light-state propagation. |
| `automation/devices/` | Shelly device gestures and ESPHome shutter-controller events. |
| `automation/hvac/` | Scheduled start/stop, external-temperature feedback, solar eligibility and holiday overheating protection. |
| `script/hvac/` | AC drying/heating routines and solar HVAC setup/wait/shutdown. |
| `automation/location/` | Request phone GPS updates when Wi-Fi and mobile home state disagree. |
| `automation/tasks/` | Database-backed recurring tasks and two-stage appliance completion. |
| `template/tasks/` | Power-derived running state and human-readable appliance state. |
| `automation/cameras/` | Empty-house motion snapshots to selected phones. |
| `script/nest/` | Mobile notifications to residents whose person entities are home. |

## Motion lighting ownership

The motion blueprint requires household presence and the global motion-light
switch, then applies optional Sleep/Guest, mode, illuminance and entry conditions.
It starts control only when the target is off or an automatic cycle is already
running. Manual lighting is not adopted into that timed cycle.

The current timeout is fixed. A rapid repeat after automatic switch-off can
leave lighting on; there is no progressive timeout multiplier. Mode/disable
cleanup branches remain behind top-level conditions, so a blocked condition can
prevent those branches from running. Root long-inactivity shutdowns are separate
rules that can also switch off manually lit areas.

`only_after_sunset` actually checks sun elevation below 10 degrees. Outdoor
instances that allow Sleep still inherit the mandatory household-presence gate.
The on-state blocker also has a target-off-for-ten-seconds bypass; its name alone
does not mean it unconditionally prevents every activation.

## Contracts worth preserving

- Shutter button `device` is a firmware name matched in an ESPHome event; Shelly
  button inputs are HA device-registry selections.
- Task blueprints consume the existing `event_remaind_task_todo` spelling and
  rely on external SQL history and insertion services.
- Solar HVAC's automation checks eligibility; its script performs and stops the
  action. Running the script directly bypasses the automation's resource checks.
- Scheduled HVAC's end time limits new starts; it does not shut down the unit.
- Light sync's later `sync_on` branch is shadowed by its first master-on branch.
  Shutdown blueprint weekend flags are OR alternatives, not restrictions on
  the explicit weekday list. Descriptions explain the current implementation.

External blueprint instances (Frigate, TV tools, LLM Vision and Music Assistant)
may reference installed files outside the tracked local families. Their instance
descriptions document selected inputs without reproducing untracked source logic.
