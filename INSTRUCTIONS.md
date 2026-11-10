# Home Assistant Tool Workflows

Follow the project preferences, protected paths, and approval rules in `AGENTS.md`.
This file describes how to discover capabilities and verify Home Assistant work.

## Discover tools before using them

- Inspect both Home Assistant MCP servers: `ha-mcp` and `homeassistant`.
  Discover their actual tools and argument schemas rather than inventing names
  or assuming tools from another installation are present.
- In Code Mode, use `search` inside `execute`, then call the exact returned
  `tools["ha-mcp"].…` or `tools.homeassistant.…` path inside `execute`.
- Use MCP tools for live states, device control, automations, troubleshooting,
  home status, and updates. Prefer scoped queries to broad state dumps.
- If an expected tool is absent, report it and do not work around its absence.
  Do not assume the cause is a reduced profile. Never bypass permission controls.
- Do not assume tool exposure proves every feature works; some operations need
  additional integrations, permissions, or installation-specific support.

## Skills and current documentation

- Before Home Assistant work, call `ha_get_skill_guide` on `ha-mcp` without a
  file argument. Read the reference files its task table requires, not all files.
- Load other matching skills only if they are actually available. Do not require
  specialist skills or MCP prompts merely because another installation had them.
- Before proposing integration configuration, consult current official Home
  Assistant documentation, using Context7 where applicable. Check the running
  version when behavior depends on the release.
- Follow server-provided tool instructions and required best-practice acknowledgments.
  Skills do not relax this project's consent or safety rules.
- Do not maintain a hard-coded deprecation/migration table here. Verify each
  proposed migration against current documentation and the installed version.

## Choose the appropriate capability

These are discovery starting points, not an exhaustive or permanent tool catalog.
Read the current schema before calling any tool.

| Task | `ha-mcp` tools | `homeassistant` tools |
|---|---|---|
| Discover entities | `ha_search` | `homeassistant__GetLiveContext` |
| State and registry metadata | `ha_get_state`, `ha_get_entity`, `ha_get_device` | `homeassistant__GetLiveContext` |
| Home overview and areas | `ha_get_overview`, `ha_list_floors_areas` | Filtered live context |
| Device control | `ha_call_service`, dedicated tools | Exposed intent and domain controls |
| History and logs | `ha_get_history`, `ha_get_logs` | Discover if needed |
| Automation/script debugging | `ha_get_automation_traces`, `ha_eval_template` | Discover if needed |
| Automations, scripts, scenes | Corresponding `ha_config_get_*` / `ha_config_set_*` tools | Explicitly exposed household scripts |
| Dashboards | `ha_config_get_dashboard`, `ha_config_set_dashboard`, `ha_get_dashboard_screenshot` | Discover if needed |
| Helpers and integrations | `ha_config_list_helpers`, `ha_config_set_helper`, `ha_get_integration`, `ha_set_integration` | Discover if needed |
| Files and YAML | `ha_read_file`, `ha_write_file`, `ha_config_get_yaml`, `ha_config_set_yaml` | Discover if needed |
| Validation and health | `ha_get_system_health` | Discover if needed |
| Backups and updates | `ha_manage_backup`, `ha_manage_updates` | Discover if needed |
| Calendar and to-do data | `ha_config_get_calendar_events`, `ha_get_todo` | `calendar__get_events`, `todo__get_items` |

Other exposed capabilities can include labels, categories, energy preferences,
HACS, themes, media search/playback, broadcasts, and vacuum area cleaning.
Discover only what the task needs; do not invoke household scripts to test access.

## Local CLI

- `hab` is installed locally, but verify availability and authentication in each
  environment. Do not assume Supervisor-token authentication or a `hab_run` tool.
- Use `hab --help` and the relevant subcommand help rather than copied command
  listings. Use `--json` for structured output.
- CLI availability does not authorize changes or bypass an absent MCP capability.

## Read, propose, validate, and verify

1. Discover entities with scoped search. Read their state and relevant metadata
   before proposing control actions. Use history for intermittent problems and
   traces/logs for automation failures; do not assume an all-in-one diagnostic exists.
2. Read existing configuration before writing. Include all existing content plus
   the approved changes when replacing a file; preserve unrelated user work.
3. Before renaming an entity, identify its consumers in automations, scripts,
   scenes, dashboards, templates, and helper/integration configuration. Do not
   assume a registry rename cascades or updates every reference.
4. Present the exact proposed change and obtain approval as required by `AGENTS.md`.
5. Always specify `entity_id` when calling `ha_call_service`. Its schema uses an
   `entity_id` argument, not the old `target={...}` wrapper. Discover service fields
   with `ha_list_services`; explicitly request response data when needed.
6. Validate using the tools actually available. For the live configuration,
   `ha_get_system_health(include="config_check")` exposes HA's configuration check.
   A live check does not validate un-deployed repository edits. Distinguish syntax
   checking from runtime validation; never claim a check that was not performed.
7. After an approved change and any approved reload/restart, read back the
   configuration or state. Use screenshots for dashboard verification when available.
   Report the outcome and wait for user verification before the next change.

Use timestamps with `Z` or a UTC offset for history and calendar requests.

## Updates and recovery

- Discover pending updates with `ha_manage_updates(action="list")`; inspect each
  target and available release notes before proposing installation.
- Follow the tool's current workflow for firmware and system updates. Do not
  assume a `watch_firmware_update` tool, job IDs, or continuous progress monitoring.
- Obtain explicit approval before installing updates, restoring or deleting
  backups, or restarting Home Assistant. Explain the concrete impact first.
- Offer a backup before major changes; do not create a full backup without consent.
  Read the backup guide before selecting the scope of a backup or restore.
- A timeout does not prove an update failed. Re-read the target's status before
  retrying; report interruptions and verify the installed version afterward.
