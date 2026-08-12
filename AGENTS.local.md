# Your own instructions for OpenCode

Rename this file to `AGENTS.local.md` (drop the `.example`) and OpenCode will read
it at the start of every session, alongside the add-on's own `AGENTS.md`.

- The add-on **never** writes to `AGENTS.local.md`. Add-on updates cannot overwrite it.
- Delete the file to stop loading it. There is no setting to toggle.
- `AGENTS.md` wins if the two ever conflict — safety rules and approval requirements
  stay in force regardless of what you put here.
- Everything in this file is sent to the model with **every** request, so keep it
  short and specific. A page of standing preferences is useful; a diary is not.
- Never put passwords, tokens, or API keys here. Reference them with `!secret` instead.

Delete the examples below and write your own.

---

## About my setup

- All Zigbee devices go through Zigbee2MQTT, not ZHA. Do not suggest ZHA workflows.
- The house has two floors: Ground floor which is the living area (living_floor) and the second floor with the bedrooms (bedrooms)
- Moreover there is an area for the exterior of the house (outside) and special areas for seasoning controls, and generic network and appliances related that affect the whole house
- Areas are named after rooms.

## How I want you to work

- New configuration goes in `packages/`, one file per feature. Do not grow
  `configuration.yaml`.
- Prefer template sensors over automations that write to `input_number` helpers.
- Name entities `<functionality>_<area>`, for example `temperature_kitchen` or `motion_sensor_office`.
- Always show me the diff before writing, even for one-line changes.

## Leave these alone

- Anything under `custom_components/` — those are managed through HACS.

## Useful context

- Some entities are seasonal like xmas lights
- Portable heater is only available during the colder months so ignore if it is unavailable