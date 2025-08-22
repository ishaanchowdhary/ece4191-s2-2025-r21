#!/usr/bin/env python3
"""
WebSocket server for:
 - Receiving velocity commands (linear v, angular w)
 - Sending back acknowledgements
 - Streaming video frames from a USB camera
"""

import asyncio
import json
import websockets
import cv2
import numpy as np

# --- Settings ---
WS_PORT = 9000

# Command mapping (adjust speeds as needed)
COMMAND_MAP = {
    "FORWARD":  {"v": 0.5, "w": 0.0},
    "REVERSE":  {"v": -0.5, "w": 0.0},
    "LEFT":     {"v": 0.0, "w": 0.8},
    "RIGHT":    {"v": 0.0, "w": -0.8},
    "STOP":     {"v": 0.0, "w": 0.0}
}

# Track connected clients
connected_clients = set()


async def handle_client(websocket):
    """Handle incoming messages from a client"""
    print("Client connected")
    connected_clients.add(websocket)

    try:
        async for message in websocket:
            # Distinguish between JSON commands and anything else
            try:
                data = json.loads(message)

                # Support both high-level commands (FORWARD) and raw v,w
                if "action" in data:
                    action = data["action"].upper()
                    if action in COMMAND_MAP:
                        vel = COMMAND_MAP[action]
                    else:
                        await websocket.send(json.dumps({"status": "error", "msg": "Invalid command"}))
                        continue
                elif "v" in data and "w" in data:
                    vel = {"v": float(data["v"]), "w": float(data["w"])}
                    action = "CUSTOM"
                else:
                    await websocket.send(json.dumps({"status": "error", "msg": "Invalid format"}))
                    continue

                # Send acknowledgement
                await websocket.send(json.dumps({
                    "status": "OK",
                    "command": action,
                    "velocities": vel
                }))

                print(f"Command: {action}, v={vel['v']}, w={vel['w']}")

            except json.JSONDecodeError:
                print("Non-JSON message ignored")

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

    finally:
        connected_clients.remove(websocket)


async def camera_stream():
    """Capture frames from USB camera and stream to clients"""
    cap = cv2.VideoCapture(0)  # change to 1 if your cam is /dev/video1

    # Optional: set resolution/FPS
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 20)

    while True:
        await asyncio.sleep(0.05)  # ~20 FPS
        ret, frame = cap.read()
        if not ret:
            continue

        # Encode frame as JPEG
        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        # Broadcast to all clients
        if connected_clients:
            await asyncio.gather(*[
                ws.send(frame_bytes) for ws in connected_clients
            ])


async def main():
    async with websockets.serve(handle_client, "0.0.0.0", WS_PORT):
        print(f"WebSocket server running on port {WS_PORT}")
        await camera_stream()  # Run camera loop forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")
