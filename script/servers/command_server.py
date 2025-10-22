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
import time, csv
import websockets
from config import *
from controllers.motor_control import set_motor_command
from controllers.ir_control import ir_on, ir_off
from controllers.servo_control import servo_up, servo_down, servo_rehome
from utils.processes import send_status_periodically, send_velocity_periodically, handle_ping
import globals
import asyncio

# Command mapping (motor directions)
COMMAND_MAP = {
    "FORWARD":              {"direction_l": 1, "direction_r": 1},
    "REVERSE":              {"direction_l": -1, "direction_r": -1},
    "LEFT":                 {"direction_l": -1, "direction_r": 1},
    "RIGHT":                {"direction_l": 1, "direction_r": -1},
    "DRIVE_STOP":           {"direction_l": 0, "direction_r": 0},
}


if LOGGING:
    # ------- CSV Logging setup -------
    path = "cmd_log.csv"
    # Open CSV and write header
    log_fh = open(path, "w", newline="")
    csv_writer = csv.writer(log_fh)
    csv_writer.writerow(["timestamp", "cmd"])

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
                if LOGGING:
                    timestamp = time.time()
                    csv_writer.writerow([timestamp, action])
                    log_fh.flush()
                # If client sends ping (for latency measurements)
                if action == "PING":
                    await handle_ping(websocket,data)
                    continue
                
                # If action is a command:
                if action in COMMAND_MAP:
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
                elif "SET_BRIGHTNESS" in action:
                    action = str.split(action)
                    globals.brightness = int(action[1])
                elif "SET_GAMMA" in action:
                    action = str.split(action)
                    globals.gamma_val = int(action[1])
                elif "SET_CONTRAST" in action:
                    action = str.split(action)
                    globals.contrast = int(action[1])
                elif "NIGHT_MODE_ON" in action:
                    globals.night_vision = True
                    globals.reset_cam_config = True
                elif "NIGHT_MODE_OFF" in action:
                    globals.night_vision = False
                    globals.reset_cam_config = True
                elif action=="CAM_MODE_1":
                        globals.cam_mode = 1
                elif action=="CAM_MODE_2":
                        globals.cam_mode = 2
                elif action == "IR_ON":
                    ir_on()
                elif action == "IR_OFF":
                    ir_off()
                elif action == "CAM_UP":
                    servo_up()
                elif action == "CAM_DOWN":
                    servo_down()
                elif action == "CAM_REHOME":
                    servo_rehome()
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