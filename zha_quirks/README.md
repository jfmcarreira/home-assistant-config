# Retained ZHA quirks

The current Zigbee deployment uses Zigbee2MQTT, not ZHA. This directory retains
the `ts0601_libht6ua.py` quirk from ZHA configuration. The root configuration still
references `/config/zha_quirks/`, and `packages/base/zha.yaml` is also present in
this repository copy.

These retained files do not document an active ZHA network. Zigbee2MQTT device
definitions and runtime entity/area mappings are maintained outside this folder.
