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
from controllers.motor_control import set_motor_command
from controllers.velocity_smoother import VelocitySmoother
from config import WHEEL_BASE, WHEEL_RADIUS
import asyncio
import time

# Command mapping (adjust speeds as needed)
COMMAND_MAP = {
    "FORWARD":    {"v": -0.5, "w": 0.0},
    "REVERSE":    {"v": 0.5, "w": 0.0},
    "LEFT":       {"v": 0.0, "w": -0.8},
    "RIGHT":      {"v": 0.0, "w": 0.8},
    "DRIVE_STOP": {"v": 0.0, "w": 0.0}
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

async def smoother_loop(): 
    """
    Function calls smoother.update() at a fixed rate and sends telemetry
    """
    global v_target, w_target, last_command, current_client

    # smoothing rate variables    
    rate_hz = 50 # to tune
    dt = 1.0 / rate_hz

    # telemetry rate
    send_rate_hz = 10 
    send_dt = 1.0 / send_rate_hz
    last_send = 0

    while True:
        v_smooth, w_smooth = smoother.update(v_target, w_target)

        # Differential drive kinematics
        L = WHEEL_BASE
        R = WHEEL_RADIUS
        v_r = (2*v_smooth + w_smooth*L) / (2*R)
        v_l = (2*v_smooth - w_smooth*L) / (2*R)

        duty_l, duty_r = set_motor_command(v_l, v_r)

        now = time.time()

        if current_client and (now - last_send) >= send_dt and duty_l != 0:
            await current_client.send(json.dumps({
                "status": "ok",
                "command": last_command,
                "velocities": {"left": v_l, "right": v_r},
                "duty_cycles": {"left": duty_l, "right": duty_r}
            }))
            

            last_send = now

        await asyncio.sleep(dt)


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
                    v_target, w_target = target["v"], target["w"]

                    # Update command variabl for telemetry 
                    last_command = action

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