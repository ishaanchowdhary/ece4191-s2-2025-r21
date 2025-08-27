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