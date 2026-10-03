# Shared ESPHome packages

Device entry points include these files with substitutions. Match the relay
package to the hardware generation: `shelly1`, `shelly25`, Plus 2PM and Gen3 2PM
variants are not interchangeable pin maps.

| Package family | Shared responsibility |
| --- | --- |
| `common`, `webserver`, `mqtt`, `use_address` | Common device/connectivity configuration. |
| `home_state` | Import household state used by device behavior. |
| `room_lights`, `motion_light`, `bathroom_controls` | Device-local light/button and bathroom behavior. |
| `shelly*`, `shelly*_lights` | Hardware definitions and corresponding lighting composition. |
| `bhonofre_cover` | Shutter motion, local buttons, opening-position helpers and HA events/services. |
| `haier_ac` | Shared climate-device firmware support. |

The shutter package exposes adjustable lower/higher positions and minimal/middle
opening services. Main buttons report double/triple actions; auxiliary buttons
report single/long/double/triple actions for HA blueprint consumers. It imports
household presence and cover-control availability, and its local enable template
permits controls when the HA API is disconnected.

Automatic room-light workflows can press a device's automatic-on button to avoid
a competing physical-button toggle. This is why an HA light automation can have
an ESPHome button entity as an output in addition to its light target.
