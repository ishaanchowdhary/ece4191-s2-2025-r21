# ECE4191 S2-25 Group R21
Github Repository for Team R21 in ECE4191 S2 2025

## SSH into pi
pw: shreklovers

## Configuration
**control_gui/config.js:**
|  |  |  |
|--|--|--|
| CONNECT_ON_PAGE_LOAD | true | Connect to WebSockets automatically on page load |

**drive/script/config.py:**
|  |  |  |
|--|--|--|
| CMD_PORT | 9000 | Websocket command port |
| VIDEO_PORT | 9001 | Websocket video port |
|--|--|--|
| WHEEL_BASE | 0.15 | Wheelbase in meters (L) |
| WHEEL_RADIUS | 0.065 | Wheel radius in meters (R) |
|--|--|--|
| PWM_FREQ | 200 | PWM frequency in Hz |
| MEASURED_MAX_WHEEL_SPEED | None | rad/s, set measured value if available |
| FALLBACK_MAX_WHEEL_SPEED | 40.0 | rad/s — conservative starting point - fallback incase MEASURED_MAX_WHEEL_SPEED is None |
| MIN_START_DUTY | 30.0 | percent, minimum duty to reliably start motor |
|--|--|--|
| CAM_INDEX | 0 |  |
| CAM_WIDTH | 640 |  |
| CAM_HEIGHT | 480 |  |
| CAM_FPS | 20 |  |
