# Home Assistant configuration

Configuration for a two-floor family home, its exterior areas, and shared energy,
water and household-task systems. House modes control automatic lighting and
lighting levels: the cats make motion alone an unsuitable signal for whether
people are awake or at home.

## Where to start

- [House layout and naming](docs/house-layout.md): physical spaces and entity-name exceptions.
- [Configuration architecture](docs/architecture.md): include graph, ownership and dependencies outside this repository.
- [House modes](appdaemon/README.md): the active AppDaemon state machine and its lighting consumers.
- [Packages](packages/README.md): purpose-specific entities and low-level operations used by the main workflows.

## Configuration entry points

| Entry point | Role |
| --- | --- |
| [`configuration.yaml`](configuration.yaml) | Loads packages, root workflows, template light/switch fragments, themes and two YAML dashboards. |
| [`automations.yaml`](automations.yaml) | Most event-driven house behavior, including room-specific blueprint instances. |
| [`scripts.yaml`](scripts.yaml) | Most user-facing routines and room-specific action scripts. |
| [`scripts/`](scripts/README.md) | Smaller reusable sequences merged into the script domain. |
| [`packages/`](packages/README.md) | Feature-specific integrations, helpers, sensors and low-level automations/scripts. |
| [`scenes.yaml`](scenes.yaml) / [`groups.yaml`](groups.yaml) | Lighting presets and configured groups. |

All files can be edited directly. The two large workflow files are also convenient
to maintain in the Home Assistant UI; this is an organizational convention, not
a division between generated and hand-written code.

## Feature directories

| Directory | Details |
| --- | --- |
| [`blueprints/`](blueprints/README.md) | Reusable lighting, HVAC, button, location and task logic. |
| [`esphome/`](esphome/README.md) | Device firmware, shared device packages and the Phosphorus energy/water node. |
| [`dashboards/`](dashboards/README.md) | Hall and living-room tablet dashboards with shared card templates. |
| [`lights/`](lights/README.md) | Template-light facades for room lighting and groups. |
| [`switches_hvac/`](switches_hvac/README.md) | Simple on/off facades over climate devices. |
| [`appdaemon/`](appdaemon/README.md) | The running `HouseMode` app. |
| [`python_scripts/`](python_scripts/README.md) | Home Assistant sandbox scripts for RF decoding and media control. |
| [`shell_scripts/`](shell_scripts/README.md) | External database, media, VM and maintenance commands. |
| [`tools/`](tools/README.md) | Offline energy-data export utility. |
| [`zha_quirks/`](zha_quirks/README.md) | Retained ZHA code; ZHA is not currently used. |

Zigbee devices currently use Zigbee2MQTT. Custom integrations are managed through
HACS, and their source is not maintained as part of this documentation.

## Reading descriptions

Automation and script descriptions are in English and are intended to be useful
in the Home Assistant UI. Existing Portuguese aliases, notification messages,
scene names and state values remain the identifiers used by the configuration.
Descriptions document the implemented conditions, timeouts and side effects;
folder READMEs explain relationships rather than repeat every description.

This repository is an editable configuration copy, not the running instance.
Live registries, integration setup, resource registration and secrets are not
reconstructed by cloning it. See the [architecture notes](docs/architecture.md)
before tracing a dependency that has no YAML definition here.
