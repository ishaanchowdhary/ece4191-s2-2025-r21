# --- Combined Command + Video WebSocket Server ---

import asyncio
import json
import websockets
import cv2
import numpy as np

WS_PORT = 9000

# --- Command Mapping ---
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
    print("Client connected")
    connected_clients.add(websocket)

    try:
        async for message in websocket:
            # Try parsing JSON (assume commands are JSON, not bytes)
            try:
                data = json.loads(message)
                action = data.get("action", "").upper()

                if action in COMMAND_MAP:
                    vel = COMMAND_MAP[action]

                    # Send acknowledgement
                    await websocket.send(json.dumps({
                        "status": "YIPPE",
                        "command": action,
                        "velocities": vel
                    }))

                    print(f"Received command: {action}")

                else:
                    await websocket.send(json.dumps({"status": "error", "msg": "Invalid command"}))

            except json.JSONDecodeError:
                print("Non-JSON message ignored")
                # Could be image bytes from client, just ignore here

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

    finally:
        connected_clients.remove(websocket)


async def camera_stream():
    cap = cv2.VideoCapture(0)  # Pi camera or USB camera

    while True:
        await asyncio.sleep(0.05)  # ~20 FPS
        ret, frame = cap.read()
        if not ret:
            continue

        # Encode as JPEG
        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        # Send to all connected clients
        if connected_clients:
            await asyncio.gather(*[
                ws.send(frame_bytes) for ws in connected_clients
            ])


async def main():
    async with websockets.serve(handle_client, "0.0.0.0", WS_PORT):
        print(f"WebSocket server running on port {WS_PORT}")
        await camera_stream()  # Run camera loop


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")
