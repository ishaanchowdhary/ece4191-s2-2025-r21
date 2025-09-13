# ECE4191 S2-25 Group R21
Github Repository for Team R21 in ECE4191 S2 2025

## SSH into pi
Open command prompt on laptop.

If Pi3:<br>
```
ssh admin@(ip address)
```
<b>password:</b> admin<br>
```
cd ece4191-s2-2025-r21
git pull
python script/main.py
```

If Pi4<br>
```
ssh master@(ip address)<br>
```
<b>password:</b> shreklovers<br>
```
cd ece4191-s2-2025-r21
git pull
python3 script/main.py
```

## Configuration

execute the following:
```
cd object_detection
python3 camera_processing.py
```
then do: <br>
**control_gui/config.js:**
|  |  |  |
|--|--|--|
| CONNECT_ON_PAGE_LOAD | true | Connect to WebSockets automatically on page load |

**drive/script/config.py:**
|  |  |  |
|--|--|--|
| CMD_PORT | 9000 | Websocket command port |
| VIDEO_PORT | 9001 | Websocket video port |
| PROCESSED_PORT | 9001 | Websocket processed video port |
|--|--|--|
| WHEEL_BASE | 0.15 | Wheelbase in meters (L) |
| WHEEL_RADIUS | 0.065 | Wheel radius in meters (R) |
|--|--|--|
| PWM_FREQ | 200 | PWM frequency in Hz |
|--|--|--|
| CAM_INDEX | 0 |  |
| CAM_WIDTH | 640 |  |
| CAM_HEIGHT | 480 |  |
| CAM_FPS | 20 |  |
