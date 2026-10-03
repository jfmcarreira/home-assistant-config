# Configuration architecture

## Loading graph

`configuration.yaml` is the Home Assistant entry point:

```text
homeassistant.packages  -> !include_dir_named packages
auth_providers         -> !include_dir_list auth_providers
automation             -> automations.yaml
script                 -> scripts.yaml
script split           -> !include_dir_merge_named scripts/
group / scene          -> groups.yaml / scenes.yaml
template.switch        -> !include_dir_list switches_hvac/
template.light         -> !include_dir_list lights/
frontend.themes        -> !include_dir_merge_named themes
lovelace.dashboards     -> hall and living-room YAML dashboard entry points
python_script          -> python_scripts/ service adapters
```

Each package YAML file is a package, with integration-domain keys inside it;
subdirectories organize features. Script fragments instead contain script IDs
at the top level and are merged into one mapping. Light/switch fragments contain
one template entity definition and are loaded as list items. A README in these
directories is not a YAML include.

## Responsibility boundaries

Most house-level workflows live in `automations.yaml` and `scripts.yaml`.
Packages supply purpose-specific behavior and the low-level operations those
workflows call. Shared blueprints factor out recurring behavior, while each
instance selects room sensors, targets and parameters.

For example:

```text
heat/sunset automation
  -> script.cover_group_action
     -> per-room control helper
     -> script.cover_group_action_worker
        -> cover service or helper script
        -> delayed last-action reason
```

Firmware-local button and relay behavior is under `esphome/`, not in the Home
Assistant package of the same name. The active AppDaemon `HouseMode` app writes
`input_select.house_mode`; template sensors expose its display state and night
flag, and lighting/tablet/security workflows consume them.

## Dependencies outside the tracked YAML

- Entities created by integrations, UI helpers, people, calendars, areas, floors,
  labels and entity-registry naming exist in the running installation. Targets
  such as `living_floor`, `bedrooms` and labels must exist there.
- HACS manages custom integrations and frontend resources. Themes and community
  frontend assets are excluded from Git even though the configuration uses them.
- Some blueprint instances refer to externally supplied blueprints, including
  Frigate notifications, TV notifications/camera feeds, Music Assistant voice
  requests and LLM Vision summaries. The tracked local blueprints are not a
  complete inventory of installed blueprints.
- The task system relies on external SQL history, a database-insertion shell
  command, and Grocy stock for selected replacement tasks. Home Assistant recorder
  history and task-completion records are different data stores.
- Fully Kiosk and Browser Mod control tablet pages/screens; Music Assistant,
  mobile-app notification services, camera integrations and LLM Vision implement
  the corresponding script actions.
- Zigbee2MQTT is currently used. ZHA entries and quirks are retained in this copy
  and should not be treated as evidence of an active ZHA deployment.

Secret values are installation-local. This documentation references mechanisms
and paths, never their contents. No deployment/synchronization mechanism is
specified here; editing this copy does not itself apply a change to Home Assistant.

## Following behavior across files

1. Start with the UI automation/script description and its configured targets.
2. For a `use_blueprint` instance, inspect the blueprint in the matching domain;
   automation and script blueprints can share a filename but have different jobs.
3. Follow script calls into `scripts/` or package `script:` sections.
4. Check templates and firmware when a target is a facade, derived sensor or
   ESPHome service rather than a directly controlled physical device.

Aliases are display text, not necessarily entity IDs: retained UI script keys
with names such as `duplicar` can have different runtime names. Without registry
evidence, a filename/key mismatch is not enough to establish a broken reference.

## Maintaining documentation

Keep descriptions on automation/script definitions and blueprint inputs, where
Home Assistant supports them. Template light/switch/sensor fragments do not gain
arbitrary `description` keys; their behavior belongs in the feature README.
Keep physical facts in the layout document and shared behavior in the owning
folder, so room-specific instances need only explain their actual parameters.

Description-only edits must preserve parsed YAML except for metadata descriptions.
Review the Git diff for unintended changes. Local YAML parsing can check syntax
and structural preservation, but cannot validate installed integrations, UI
registries or the running Home Assistant configuration.
