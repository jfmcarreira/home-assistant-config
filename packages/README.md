# Purpose-specific packages

Each YAML file is loaded through `homeassistant.packages` in the root
configuration. These files hold feature-specific entities and low-level behavior
used by the main automations and scripts; they are directly maintained alongside
the root workflows.

| Folder | Responsibility |
| --- | --- |
| [`base/`](base/README.md) | Shared persistence, notifications, tablet integration and RF bridge wiring. |
| [`covers/`](covers/README.md) | Shutter groups, per-room policy helpers, group dispatch and action tracking. |
| [`dashboards/`](dashboards/README.md) | Return tablets to their configured home dashboard. |
| [`devices/`](devices/README.md) | Assistant speakers, baby-monitor derived entities and vacuum selection. |
| [`energy/`](energy/README.md) | Power attribution, battery estimates and electricity pricing. |
| [`helpers_entities/`](helpers_entities/README.md) | Calendar/time-derived inputs used by climate decisions. |
| [`hvac/`](hvac/README.md) | Portable heater/dehumidifier models and AC reset operations. |
| [`rules/`](rules/README.md) | Shared task-reminder event production. |
| [`sensors/`](sensors/README.md) | Derived house, person, room, environmental and stock state. |
| [`tasks/`](tasks/README.md) | Due-task and appliance states backed by completion history. |
| [`utilities/`](utilities/README.md) | Manual billing-meter readings and database writes. |
| [`water/`](water/README.md) | Measured flow/volume totals and portable-meter representation. |
| [`water_heater/`](water_heater/README.md) | Electric thermostat and derived solar-thermal heating state. |

Adding a helper here does not automatically add it to a root workflow or dashboard.
Entity IDs are the connections between these layers; integration-provided entities
and UI helpers need not have a definition in the same package.
