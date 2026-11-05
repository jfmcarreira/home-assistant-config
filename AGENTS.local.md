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