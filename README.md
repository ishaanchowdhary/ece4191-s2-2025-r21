# ECE4191 S2-25 Group R21
Github Repository for Team R21 in ECE4191 S2 2025

## SSH into pi
Open command prompt on laptop.

If Pi3:<br>
ssh admin@(ip address)<br>
password: admin<br>
cd ece4191-s2-2025-r21<br>
git pull<br>
python script/main.py<br>

If Pi4<br>
ssh master@(ip address)<br>
pw: shreklovers<br>
cd ece4191-s2-2025-r21<br>
git pull<br>
python3 script/main.py<br>


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
