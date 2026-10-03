# Reusable script fragments

The root configuration merges this directory into the script domain alongside
`scripts.yaml`. Each file contains script IDs directly, without a `script:` wrapper.
Main user-facing routines live in the root file and call these smaller sequences.

| Fragment | Contract |
| --- | --- |
| `helpers/house_mode.yaml` | Manual mode cycling; changes the same selector that AppDaemon manages. |
| `helpers/sequence_door_open.yaml` | Wait through kitchen-door opening/closing and update the shared progress message; timeouts continue. |
| `helpers/sequence_leaving_home_lights.yaml` | Night-only exterior exit path with separate door and gate waits. |
| `helpers/sequence_notify_tasks.yaml` | Speak the dishwasher-start reminder when enabled. |
| `helpers/task_notifications.yaml` | Clear selected task-notification tags for residents who are away. |
| `helpers/run_actions_later.yaml` | Delay simple service calls; supports hours/minutes/seconds and does not persist across restart. |
| `actions/tv_shows.yaml` | User-facing wrapper over the Netflix Python-script adapter. |

## Call and timeout semantics

A direct `action: script.<name>` waits for the called script. `script.turn_on`
starts it asynchronously. Departure/doorbell routines use both forms, so changing
the call form changes ordering even if the target script stays the same.

`input_text.script_step_message` is shared progress state, not a per-run variable.
Several root workflows and the cleanup automation write it. An aborting wait may
skip local cleanup; the root cleanup automation covers selected routines.

Descriptions on these definitions appear in Home Assistant's script UI. Scripts
without an alias still use their configured IDs; documentation does not rename them.
