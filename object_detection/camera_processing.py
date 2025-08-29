"""
camera_processing.py
-------------
Receives JPEG frames from WebSocket clients (port 9001),
runs YOLO detection on each frame, and forwards the
annotated frames to another WebSocket server (port 9002).

Dependencies:
- ultralytics (YOLOv8)
- cv2
- numpy
- websockets
- asyncio

Usage:
    python camera_processing.py
"""

import asyncio
import cv2
import numpy as np
import websockets
from ultralytics import YOLO

# ----------------------------
# Config
# ----------------------------
IN_PORT = 9001   # incoming frames
OUT_PORT = 9002  # outgoing frames
MODEL_PATH = "models/best_v1.pt"  # change if you trained your own model

# Track connected clients for output
output_clients = set()

# Load YOLO model
model = YOLO(MODEL_PATH)


# ----------------------------
# Handle incoming frames
# ----------------------------
async def handle_incoming(websocket):
    print(f"[INPUT] Client connected: {websocket.remote_address}")
    try:
        async for message in websocket:
            try:
                # Convert bytes -> numpy -> BGR frame
                img_array = np.frombuffer(message, np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                if frame is None:
                    continue

                # Run YOLO inference
                results = model(frame, verbose=False)
                annotated = results[0].plot()

                # Encode back to JPEG
                ret_enc, buffer = cv2.imencode(".jpg", annotated)
                if not ret_enc:
                    continue
                frame_bytes = buffer.tobytes()

                # Broadcast to connected output clients
                if output_clients:
                    await asyncio.gather(*[
                        ws.send(frame_bytes) for ws in list(output_clients)
                    ])
            except Exception as e:
                print(f"[ERROR] Failed to process frame: {e}")
    finally:
        print(f"[INPUT] Client disconnected: {websocket.remote_address}")


# ----------------------------
# Manage output connections
# ----------------------------
async def handle_output(websocket):
    print(f"[OUTPUT] Viewer connected: {websocket.remote_address}")
    output_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        output_clients.remove(websocket)
        print(f"[OUTPUT] Viewer disconnected: {websocket.remote_address}")


# ----------------------------
# Main entry
# ----------------------------
async def main():
    in_server = await websockets.serve(handle_incoming, "0.0.0.0", IN_PORT)
    out_server = await websockets.serve(handle_output, "0.0.0.0", OUT_PORT)

    print(f"[INFO] Listening for input on ws://0.0.0.0:{IN_PORT}")
    print(f"[INFO] Serving processed stream on ws://0.0.0.0:{OUT_PORT}")

    await asyncio.gather(in_server.wait_closed(), out_server.wait_closed())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user.")
    except asyncio.CancelledError:
        pass
