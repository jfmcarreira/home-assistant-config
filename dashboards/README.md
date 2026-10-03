# Tablet dashboards

`configuration.yaml` registers two YAML dashboards:

| Folder | Dashboard key | Display location |
| --- | --- | --- |
| `dashboard-living-room/` | `dashboard-living-room` | Living-room Lenovo tablet. |
| `dashboard-hall/` | `dashboard-hall` | Upstairs hall Fire tablet. |

Each `dashboard-*.yaml` entry point includes a control panel and feature panels.
Navigation uses `custom:state-switch` with the URL hash, rather than separate
Lovelace views for each feature. Kiosk mode hides the header; layouts are tuned
to tablet dimensions.

## Shared components

- `common/button-card-templates.yaml` supplies reusable button-card definitions.
- `common/declutering.yaml` supplies decluttering templates. Its existing filename
  spelling is used by both entry points.
- Individual `panel-*.yaml` files contain the room/device controls and main-screen
  sections. Hall includes house/WC panels; living room includes a tasks panel and
  separate main-left/main-right sections.

Frontend dependencies include button-card, decluttering-card, layout-card,
state-switch, Mushroom, vertical-stack-in-card, auto-entities, fold-entity-row,
Bubble Card, compact-power-card and mass-player-card, plus kiosk-mode. Resources
must be installed/registered in Home Assistant; card references do not install them.

Bubble Card's module definitions are separate from dashboard panels; see
[`bubble_card/`](../bubble_card/README.md) for the empty global module and retained
default-styling module.

Behavioral page resets are in [`packages/dashboards/`](../packages/dashboards/README.md).
Root automations control screen/motion/timeouts; Browser Mod provides doorbell
camera popups. Displaying a room card does not mean its entity is physically in
that dashboard's room.
