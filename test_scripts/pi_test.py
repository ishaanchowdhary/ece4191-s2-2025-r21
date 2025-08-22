# This Python script will be used for testing connectivity with the client GUI

import asyncio
import json
import websockets
import cv2
import base64

# --- Settings ---
WS_PORT = 9000
CAMERA_INDEX = 0


# Command mapping (adjust speeds as needed)
COMMAND_MAP = {
    "FORWARD":  {"v": 0.5, "w": 0.0},
    "REVERSE":  {"v": -0.5, "w": 0.0},
    "LEFT":     {"v": 0.0, "w": 0.8},
    "RIGHT":    {"v": 0.0, "w": -0.8},
    "STOP":     {"v": 0.0, "w": 0.0}
}


# --- Global state ---
clients = set()
camera_active = False


async def handle_client(websocket, path):
    print("Client connected")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                action = data.get("action", "").upper()

                if action in COMMAND_MAP:

                    # Send acknowledgement
                    await websocket.send(json.dumps({
                        "status": "YIPPE",
                        "command": action,
                        "velocities": {"left": "v_l", "right": "v_r"}
                    }))

                    #for testing 
                    print("Received:", action)

                else:
                    print("Unknown command:", action)
                    await websocket.send(json.dumps({"status": "error", "msg": "Invalid command"}))

            except json.JSONDecodeError:
                print("Invalid JSON received")
                await websocket.send(json.dumps({"status": "error", "msg": "Bad JSON"}))

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")


async def camera_stream():
    """Continuously capture frames and send to clients if active"""
    global camera_active
    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        print("Could not open camera :()")
        return

    while True:
        await asyncio.sleep(0.05)  # ~20 FPS
        if camera_active and clients:
            ret, frame = cap.read()
            if not ret:
                continue

            # Encode as JPEG → Base64 for WebSocket
            _, jpeg = cv2.imencode(".jpg", frame)
            frame_b64 = base64.b64encode(jpeg.tobytes()).decode("utf-8")

            msg = json.dumps({"camera_frame": frame_b64})

            # Send to all connected clients
            websockets.broadcast(clients, msg)

    cap.release()

async def main():
    async with websockets.serve(handle_client, "0.0.0.0", WS_PORT):
        print(f"WebSocket server running on port {WS_PORT}")
        #await asyncio.Future()  # run forever
        await camera_stream()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")