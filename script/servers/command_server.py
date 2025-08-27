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

# Command mapping (adjust speeds as needed)
COMMAND_MAP = {
    "FORWARD":    {"v": 0.5, "w": 0.0},
    "REVERSE":    {"v": -0.5, "w": 0.0},
    "LEFT":       {"v": 0.0, "w": 0.8},
    "RIGHT":      {"v": 0.0, "w": -0.8},
    "DRIVE_STOP": {"v": 0.0, "w": 0.0}
}

# Velocity smoother instance
smoother = VelocitySmoother(max_accel=0.5, max_ang_accel=2.0, rate_hz=50)

async def handle_client(websocket, path):
    """Handle a single command WebSocket client (keeps original signature)."""
    print("Command client connected")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                action = data.get("action", "").upper()

                if action in COMMAND_MAP:
                    target = COMMAND_MAP[action]

                    # Smooth velocities
                    v_smooth, w_smooth = smoother.update(target["v"], target["w"])

                    # Differential drive equations
                    L = WHEEL_BASE
                    R = WHEEL_RADIUS
                    v_r = (2*v_smooth + w_smooth*L) / (2*R)
                    v_l = (2*v_smooth - w_smooth*L) / (2*R)

                    set_motor_command(v_l, v_r)

                    # Send acknowledgement
                    await websocket.send(json.dumps({
                        "status": "ok",
                        "command": action,
                        "velocities": {"left": v_l, "right": v_r}
                    }))

                    print(f"Command: {action} | v_l={v_l:.2f}, v_r={v_r:.2f}")

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