# Wall tablet – dashboard design spec

Device observations collected over ADB on 2026-11-08. Target: **landscape**.

## Device

| | |
|---|---|
| Model | Lenovo Tab **TB311FU** |
| RAM | ~4 GB |
| Panel | **1920 x 1200 px** in landscape, **60 Hz** |
| Power | Always on USB charge |
| Kiosk | Kiosk Satellite; landscape locked, status and navigation bars hidden |
| Content | Portuguese; Europe/Lisbon time zone |

## Observed display settings

- Density override: **262 dpi**; Android font scale: **1.15**.
- Estimated DPR: **1.64**; estimated viewport: **1172 x 733 CSS px**.
- Confirm actual `innerWidth`, `innerHeight`, and `devicePixelRatio` on the tablet
  before treating these estimates as layout limits.

## Layout and performance

- Aspect ratio: **16:10**, not 16:9.
- Use `100dvh` / `100dvw`; avoid scrolling for the main view.
- Account for plugin bars with `--ks-content-inset-top`, `-right`, `-bottom`,
  and `-left`, each with a `0px` fallback.
- Touch targets: **at least 48 CSS px**. Respect the configured font scale.
- Avoid backdrop blur, large shadows, and large animated gradients.
- Prefer `transform` / `opacity` animations; split heavy content into views.
- Kiosk Satellite handles dashboard rotation and the screensaver; do not duplicate them.

## Kiosk Satellite references

- [Custom pages](https://kiosksatellite.com/docs/custom-pages/)
- [JavaScript API](https://kiosksatellite.com/docs/js-api/)
- [Dashboard links](https://kiosksatellite.com/docs/dashboard-links/)

Shared HA access requires a custom page and **Share Home Assistant connection**
to be enabled. Only use trusted pages: they inherit the kiosk user's HA permissions.
