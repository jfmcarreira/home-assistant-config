# Bubble Card modules

This directory holds Bubble Card module configuration, separate from Lovelace
panel YAML and HACS's installed card source.

- `config.yaml` records completed module migration metadata.
- `modules/default.yaml` defines an empty globally enabled customization module;
  its `code` is currently empty, so it supplies no additional styling or JavaScript.
- `modules/home-assistant-default.yaml` contains the upstream Home Assistant
  default-styling module, including CSS based on Home Assistant theme variables.

Module presence alone does not mean every card applies it. Card/module selection
is managed through Bubble Card; the default-styling module is not marked globally
enabled in its file. Dashboard Bubble Card usage is under
[`dashboards/`](../dashboards/README.md).
