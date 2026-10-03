# Home Assistant Python-script adapters

The root `python_script:` integration exposes these sandbox scripts as services.
They receive the service `data` object and use Home Assistant's injected `hass`
API; they are not standalone Python applications.

| Script | Purpose |
| --- | --- |
| `rf_bridge_demux.py` | Map RF codes to washing/dryer door, kitchen-fan and gate-bell MQTT topics; unknown codes use a separate topic. |
| `netflix_play_show.py` | Search/play a show using a timed webOS remote-button sequence, with living-room TV as the default target. |
| `living_room_media_center_remote.py` | Living-room media remote adapter. |
| `change_meo_box_channel.py`, `meo_box_reset_show.py` | MEO box channel/program control adapters. |
| `date_countdown.py` | Date-countdown helper logic. |

RF decoding is called by `packages/base/rf_demux.yaml`. Netflix is wrapped by
`scripts/actions/tv_shows.yaml`; its navigation depends on the TV application's
menu layout and fixed button timings, not a catalog-search API.
