"""
command_server.py
-----------------
WebSocket server for handling commands.

This module:
- Accepts JSON-encoded commands over WebSocket from remote clients.
- Maps high-level actions (FORWARD, REVERSE, LEFT, RIGHT, DRIVE_STOP) to left/right motor directions.
- Updates motor commands via the motor_control module.
- Supports dynamic adjustment of minimum and maximum PWM duty cycles via "SET_DUTY" commands.
- Maintains the last received command for telemetry or logging purposes.

Main Functions:
- handle_client(websocket, path)
    Asynchronous function to handle a single WebSocket client connection.
    Processes incoming JSON commands and updates motor directions or PWM limits.

Dependencies:
- websockets: For asynchronous WebSocket communication.
- json: For decoding/encoding JSON messages.
- controllers.motor_control: To send motor direction commands.
- globals: For runtime configuration (e.g., min/max duty cycles).
"""

import json
import websockets
from config import *
from controllers.motor_control import set_motor_command
from utils.processes import send_status_periodically, send_velocity_periodically, handle_ping
import globals
import asyncio

# Command mapping (adjust speeds as needed)
COMMAND_MAP = {
    "FORWARD":              {"direction_l": 1, "direction_r": 1},
    "REVERSE":              {"direction_l": -1, "direction_r": -1},
    "LEFT":                 {"direction_l": -1, "direction_r": 1},
    "RIGHT":                {"direction_l": 1, "direction_r": -1},
    "DRIVE_STOP":           {"direction_l": 0, "direction_r": 0},
    "NIGHT_MODE_ON":        True,
    "NIGHT_MODE_OFF":       False,
    "INCREASE_BRIGHTNESS":  1,
    "DECREASE_BRIGHTNESS":  -1,
    "INCREASE_CONTRAST":    1,
    "DECREASE_CONTRAST":    -1,
    "INCREASE_GAMMA":       1,
    "DECREASE_GAMMA":       -1,
    "CAM_MODE_1":           1,
    "CAM_MODE_2":           2,
    "CAM_MODE_3":           3,
}


# Websocket
current_client = None 

async def handle_client(websocket, path):
    """Handle a single command WebSocket client (keeps original signature)."""
    print("Command client connected")

    global current_client # so variables can be modified

    current_client = websocket
    # Start background task
    status_task = asyncio.create_task(send_status_periodically(websocket))
    velocity_task = asyncio.create_task(send_velocity_periodically(websocket))

    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                action = data.get("action", "").upper()

                # If client sends ping (for latency measurements)
                if action == "PING":
                    await handle_ping(websocket,data)
                    continue
                
                # If action is a command:
                if action in COMMAND_MAP:
                    target = COMMAND_MAP[action]

                    # If action is a vision command
                    if action=="NIGHT_MODE_ON" or action=="NIGHT_MODE_OFF":
                        globals.night_vision = target
                        globals.reset_cam_config = True
                    elif action=="INCREASE_BRIGHTNESS" or action=="DECREASE_BRIGHTNESS":
                        globals.brightness += target
                        globals.brightness = max(globals.brightness,0)
                        globals.brightness = min(globals.brightness,100)
                    elif action=="INCREASE_CONTRAST" or action=="DECREASE_CONTRAST":
                        globals.contrast += target
                        globals.contrast = max(globals.contrast,0)
                        globals.contrast = min(globals.contrast,100)
                    elif action=="INCREASE_GAMMA" or action=="DECREASE_GAMMA":
                        globals.gamma_val += target
                        globals.gamma_val = max(globals.gamma_val,0)
                        globals.gamma_val = min(globals.gamma_val,300)
                    elif action=="CAM_MODE_1" or action=="CAM_MODE_2" or action=="CAM_MODE_3":
                        globals.cam_mode = target
                    
                    # If action is a motor command
                    else:
                        target = COMMAND_MAP[action]
                        # Extract directions and set motor command
                        direction_l, direction_r = target["direction_l"], target["direction_r"]
                        set_motor_command(direction_l, direction_r)

                # If action is to set new duty cycle limits:
                elif "SET_DUTY" in action:
                    # stop motors before changing duty
                    set_motor_command(0, 0)  
                    # Update minimum starting duty cycle
                    action = str.split(action)
                    new_duty = [int(action[1]), int(action[2])]
                    globals.min_duty = min(new_duty)
                    globals.max_duty= max(new_duty)
                    print(f"Updated duty cycle limits: MIN_START_DUTY={globals.min_duty}, MAX_DUTY={globals.max_duty}")
                else:
                    print("Unknown command:", action)
                    await websocket.send(json.dumps(
                        {"status": "error", "msg": "Invalid command"}
                    ))

            except json.JSONDecodeError:
                print("Invalid JSON received")
                await websocket.send(json.dumps(
                    {"status": "error", "msg": "Bad JSON"}
                ))

    except websockets.exceptions.ConnectionClosed:
        print("Command client disconnected")
        set_motor_command(0, 0)  # stop motors on disconnect
    finally:
        status_task.cancel()  # stop background task when client disconnects
        velocity_task.cancel()