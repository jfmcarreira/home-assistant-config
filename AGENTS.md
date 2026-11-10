# Home Assistant Project Rules

Project-specific preferences and safety rules live here. Read `INSTRUCTIONS.md`
for tool discovery, documentation, validation, and verification workflows.
If the files conflict, these consent, scope, and safety rules take precedence.

## Environment

- Determine the actual working directory and whether it is a repository checkout
  or the live Home Assistant configuration. Do not assume `/homeassistant`.
- Ordinary file-editing tools may be used in a repository checkout, subject to
  the approval rules below. Editing a checkout does not authorize deployment.
- Use MCP tools for current Home Assistant information; local files are not
  evidence of runtime state.
- If `AGENTS.local.md` is provided, follow it unless it conflicts with this file.

## Home context

- All Zigbee devices use Zigbee2MQTT, not ZHA. Do not suggest ZHA workflows.
- Ground floor / living area: `living_floor`. Second floor / bedrooms: `bedrooms`.
- Areas are named after rooms. There is also an exterior area (`outside`) and
  special areas for seasonal controls, networking, and whole-house appliances.
- Some entities are seasonal, such as Christmas lights.
- The portable heater is only available during colder months; ignore it if unavailable.

## Configuration preferences

- New configuration goes in `packages/`, one file per feature. Do not grow
  `configuration.yaml`.
- Prefer template sensors over automations that write to `input_number` helpers.
- Name entities `<functionality>_<area>`, for example `temperature_kitchen`
  or `motion_sensor_office`.
- Leave everything under `custom_components/` alone; it is managed through HACS.

## Consent and scope

1. Do exactly what the user requests. Do not add features, refactor working
   configuration, clean up unrelated code, or fix unmentioned issues.
2. Before writing, editing, or deleting any file, show the exact diff, even for
   a one-line change, and wait for explicit confirmation. Do not write first.
3. If the request is ambiguous, ask questions and present options. Never guess
   the user's intent.
4. Investigations and troubleshooting are read-only. Present findings and
   recommendations, then wait for instructions before making changes.
5. Make one approved change at a time, using the minimum change needed. Show
   what changed and let the user verify before proceeding to the next step.
6. Obtain confirmation before controlling devices or changing runtime configuration.
7. If the user declines a suggestion, do not repeat it, apply it, or argue for it.

## Safety and protected paths

- Never expose `secrets.yaml` contents or include API keys, tokens, or passwords
  in responses or persistent notes.
- Never directly access Home Assistant internal state or parse internal JSON
  for entity, device, or area information. Never attempt to modify Home
  Assistant's internal databases or registries.
- Prefer MCP runtime queries over internal file access.

| Protected path | Use instead |
|---|---|
| `.storage/` | MCP entity, device, and area queries |
| `.cloud/` | Home Assistant-managed cloud functionality |
| `deps/` | Home Assistant-managed dependencies |
| `tts/` | Home Assistant-managed TTS functionality |
| `home-assistant_v2.db` | MCP history and logbook queries |
| `home-assistant.log` | MCP log queries |

- Only inspect or modify `/addons` or `/addon_configs` when explicitly requested.
  Treat `/addon_configs` as sensitive.
- Warn whether a proposed change requires a reload or restart before applying it.
- Suggest a backup before major modifications. Check configuration validity
  when possible, and report any validation that could not be performed.

## Existing decisions

- Do not assume installation briefings or decision digests are injected.
  Any supplied snapshot is orientation, not live state.
- Respect supplied decisions. If a request conflicts with one, explain the
  conflict and ask before reversing it.
- If decision-recall tools are available, consult them before changing something
  that may be deliberate. An empty search is not proof that no decision exists;
  try different wording or an unfiltered lookup. Report unavailable recall tools.
- Before recording a permanent decision, show its exact wording and obtain
  explicit approval; obtain separate approval for pinning. Do not store session
  logs, facts already in configuration, or secrets. Do not assume notes persist
  or are injected into future sessions.
