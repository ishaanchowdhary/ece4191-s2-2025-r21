"""
camera_stream.py
-----------------
Captures video frames from a USB camera and broadcasts them to connected clients.

Responsibilities:
- Initialize camera using OpenCV.
- Capture frames, encode as JPEG, and send to all connected clients.
- Run continuously at a fixed frame rate.

Main Function:
- camera_stream(): Infinite loop capturing and broadcasting frames.

Dependencies:
- cv2 (OpenCV) for camera access and JPEG encoding
- servers.video_server for list of connected clients

Usage:
    await camera_stream()
"""

import asyncio
import cv2

from servers.video_server import video_clients
from servers.socket_server import socket_clients
from config import CAM_INDEX, CAM_WIDTH, CAM_HEIGHT, CAM_FPS, RUN_SOCKET_SERVER
import utils.video_enhancer as enhance
import globals

async def camera_stream():
    """Continuously capture and broadcast frames."""
    # Use V4L2 backend if available (keeps your original intent)
    cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, CAM_FPS)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 0)  # minimize latency

    # Sleep interval approximate to CAM_FPS
    sleep_dt = 1.0 / CAM_FPS if CAM_FPS > 0 else 0.05

    while True:
        await asyncio.sleep(sleep_dt)
        ret, frame = cap.read()
        if not ret:
            # don't spam, short pause and continue
            await asyncio.sleep(0.1)
            continue
        # Apply image enhancer
        if globals.night_vision:
            # Reset to default parameters
            if globals.reset_cam_config:
                globals.brightness = globals.BRIGHTNESS
                globals.contrast = globals.CONTRAST
                globals.gamma_val = globals.GAMMA_VAL
                globals.reset_cam_config = False
                globals.cam_mode = 1
            # Enhance frame
            frame = enhance.enhance_frame(frame, mode=globals.cam_mode, brightness=globals.brightness, contrast=globals.contrast, gamma_val=globals.gamma_val)

        # Encode to JPEG
        ret_enc, buffer = cv2.imencode(".jpg", frame)
        if not ret_enc:
            continue
        frame_bytes = buffer.tobytes()

        # Broadcast to all connected clients
        if video_clients:
            # gather ensures concurrent sends; preserve original behavior
            await asyncio.gather(*[
                ws.send(frame_bytes) for ws in list(video_clients)
            ])
        
        # Broadcast to raw socket clients
        if socket_clients and RUN_SOCKET_SERVER:
            for client in list(socket_clients):
                try:
                    # Prefix the frame with 4-byte length header
                    client.write(len(frame_bytes).to_bytes(4, byteorder='big') + frame_bytes)
                    await client.drain()
                except Exception as e:
                    print(f"[Raw Socket] Failed to send to client: {e}")
                    socket_clients.remove(client)