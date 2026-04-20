# Kaleidoscope Home Assistant Integration

This is a custom component implementation to connect our custom
[Kaleidoscope](https://github.com/mrd0ll4r/kaleidoscope/)
lighting to Home Assistant.

It discovers fixtures, programs, and their parameters,
creates matching devices in Home Assistant,
and makes them controllable.
All fixtures are exposed as Home Assistant `light`s,
which allows turning them on and off.
Additionally, each fixture contains a program selector
and parameters for all available programs.

This repository also contains a dashboard for our specific setup
in `dashboards/`.
The cards use [auto-entities](https://github.com/thomasloven/lovelace-auto-entities),
for per-fixture cards with dynamic parameter controls.
Only controls for the currently-running program are shown.
Entities for all parameters are present at all times,
to allow setting them programmatically before switching to a new program.

## Installation

### Kaleidoscope Integration

1. Create `<HA config dir>/custom_components/kaleidoscope_lighting`
2. Copy `kaleidoscope_lighting/*` to `<HA config dir>/custom_components/kaleidoscope_lighting`
3. Restart Home Assistant
4. Connect to Kaleidoscope via Settings -> Devices -> Add Integration -> Kaleidoscope
5. The integration discovers fixtures, programs, and parameters.
6. Assign locations and other metadata to newly-discovered devices as usual.

### Dashboard

1. Install HACS
2. Install `auto-entities` via HACS, see [here](https://github.com/thomasloven/lovelace-auto-entities)
3. Add a new dashboard: Settings -> Dashboards -> Add Dashboard -> From Scratch
4. In the dashboard, add device cards as needed: Edit (top right) -> Add Card -> Manual (all the way at the bottom)
5. Edit/Paste appropriate YAML from `cards/`