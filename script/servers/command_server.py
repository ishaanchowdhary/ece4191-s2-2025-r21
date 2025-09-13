"""
command_server.py
-------------------
WebSocket server for handling motion commands from remote clients.
-------------------

- Receive JSON-encoded commands via WebSocket.
- Map actions (FORWARD, REVERSE, LEFT, RIGHT, DRIVE_STOP) to target velocities.
- Use VelocitySmoother to limit acceleration.
- Convert velocities to wheel commands and call motor controller.

Usage:
    await websockets.serve(handle_client, "0.0.0.0", CMD_PORT)
"""

import json
import websockets
from config import *
from controllers.motor_control import set_motor_command
from controllers.velocity_smoother import VelocitySmoother
import globals
import asyncio
import time

# Command mapping (adjust speeds as needed)
COMMAND_MAP = {
    "FORWARD":    {"direction_l": 1, "direction_r": 1},
    "REVERSE":    {"direction_l": -1, "direction_r": -1},
    "LEFT":       {"direction_l": -1, "direction_r": 1},
    "RIGHT":      {"direction_l": 1, "direction_r": -1},
    "DRIVE_STOP": {"direction_l": 0, "direction_r": 0}
}

# Shared variables
# Velocity smoother instance
smoother = VelocitySmoother(max_accel=5, max_ang_accel=10.0, rate_hz=50)

# Target velocity variables
v_target, w_target = 0.0, 0.0

# Last command variable for telemetry
last_command = "DRIVE_STOP"

# Websocket
current_client = None 

async def handle_client(websocket, path):
    """Handle a single command WebSocket client (keeps original signature)."""
    print("Command client connected")

    global v_target, w_target, last_command, current_client # so variables can be modified

    current_client = websocket
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                action = data.get("action", "").upper()

                if action in COMMAND_MAP:
                    target = COMMAND_MAP[action]

                    # Update target velocities
                    direction_l, direction_r = target["direction_l"], target["direction_r"]
                    set_motor_command(direction_l, direction_r)
                    # Update command variabl for telemetry 
                    last_command = action
                elif "SET_DUTY" in action:
                    set_motor_command(0, 0)  # stop motors before changing duty
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