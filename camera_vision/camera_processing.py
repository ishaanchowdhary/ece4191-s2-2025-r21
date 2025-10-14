#!/usr/bin/env python3
"""
camera_processing.py
-------------
Subscribes to raw JPEG frames from VIDEO_PORT (9001),
runs YOLO detection on each frame, and serves annotated
frames to connected clients on OUT_PORT (9002).

Dependencies:
- ultralytics (YOLOv8)
- cv2
- numpy
- websockets
- asyncio
"""

import asyncio
import cv2
import os
import numpy as np
import websockets
from ultralytics import YOLO

# ----------------------------
# Config
# ----------------------------
RPI_IP = os.environ.get("RPI_IP", "172.20.10.2").strip()  # fallback default
IN_URI = f"ws://{RPI_IP}:9001"  # raw frames from camera_stream.py
OUT_PORT = 9002                 # serve processed frames here
MODEL_PATHS = ["models/NoIR/Archive/best_NoIR_v1_sq.pt",
               "models/NoIR/square/best_v5_sq_NoIR.pt",
               "models/NoIR/rectangle/best_v5_rt_NoIR.pt",
               "models/NoIR/rectangle/best_v9_rt_NoIR.pt"]
MODEL_PATH_IDX = 1

# Track connected output clients
output_clients = set()

# Load YOLO model once
model = YOLO(MODEL_PATHS[MODEL_PATH_IDX])


# ----------------------------
# Output server (for browsers/viewers)
# ----------------------------
async def handle_output(websocket):
    print(f"[OUTPUT] Viewer connected: {websocket.remote_address}")
    output_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        output_clients.discard(websocket)
        print(f"[OUTPUT] Viewer disconnected: {websocket.remote_address}")


# ----------------------------
# Processing loop
# ----------------------------
async def process_stream():
    """Subscribe to raw frames on IN_URI, run YOLO, broadcast annotated frames."""
    print(f"[INPUT] Connecting to raw stream at {IN_URI}...")
    while True:
        try:
            async with websockets.connect(IN_URI, max_size=2**24) as ws:  # allow big frames
                print("[INPUT] Connected to raw stream")
                async for message in ws:
                    try:
                        # Convert bytes -> numpy -> BGR frame
                        img_array = np.frombuffer(message, np.uint8)
                        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        if frame is None:
                            continue
                        if output_clients:
                            try:
                                # Run YOLO inference
                                results = model.predict(frame_bgr, verbose=False)
                                annotated = results[0].plot(img=frame)

                                # Encode back to JPEG
                                ret_enc, buffer = cv2.imencode(".jpg", annotated)
                                if not ret_enc:
                                    continue
                                frame_bytes = buffer.tobytes()

                                # Broadcast to connected output clients
                                dead = []
                                for client in list(output_clients):
                                    try:
                                        await client.send(frame_bytes)
                                    except:
                                        dead.append(client)
                                for d in dead:
                                    output_clients.discard(d)
                            except Exception as e:
                                print(f"[ERROR] YOLO processing failed: {e}")
                            else:
                                pass
                    except Exception as e:
                        print(f"[ERROR] Processing frame failed: {e}")
        except Exception as e:
            print(f"[WARN] Lost connection to raw stream ({e}), retrying in 2s...")
            await asyncio.sleep(2)


# ----------------------------
# Main entry
# ----------------------------
async def main():
    # Start output WebSocket server
    async with websockets.serve(handle_output, "0.0.0.0", OUT_PORT):
        print(f"[INFO] Serving processed stream on ws://0.0.0.0:{OUT_PORT}")

        # Start processing loop (never returns)
        await process_stream()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user.")
