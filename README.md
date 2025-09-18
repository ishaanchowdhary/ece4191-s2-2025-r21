
# ECE4191 S2-25 Group R21
Github Repository for Team R21 in ECE4191 S2 2025

## Setup Steps
Before startup, you must know the IP address of the Raspberry Pi

**SSH into Raspberry Pi & Run Script**

Open command prompt on laptop. 
| RPi 3  |  RPi 4 |
|---|---|
| `ssh admin@<IP address>`  |  `ssh master@<IP address>` |
| `pw: admin`  |  `pw: shreklovers` |
| `cd ece4191-s2-2025-r21`<br>`git pull`<br>`python script/main.py`  |  `cd ece4191-s2-2025-r21`<br>`git pull`<br>`python script/main.py` |

**Start Object Detection**

In a new command prompt window, navigate to the local github repo.
`
cd object_detection`<br>`
python3 camera_processing.py
`

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


## Authors

- [@JaidenMcD](https://github.com/JaidenMcD)
- [@ishaanchowdhary](https://github.com/ishaanchowdhary)
- [@eeenr](https://github.com/eeenr)
- [@mgil-0015](https://github.com/mgil-0015)
- [@livg000](https://github.com/livg000)
- [@ahay0015](https://github.com/ahay0015)




