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

"""TESTING """

import asyncio
import cv2
import numpy as np
import json
from picamera2 import Picamera2

from servers.video_server import video_clients
from servers.socket_server import socket_clients
from config import CAM_WIDTH, CAM_HEIGHT, CAM_FPS, RUN_SOCKET_SERVER, JPEG_QUALITY
import utils.video_enhancer as enhance
import globals


async def camera_stream():
    """Continuously capture and broadcast frames using Picamera2."""   
    # Initialize picam2 variable    
    picam2 = None
    # Initialize camera
    try:
        cam_info = Picamera2().global_camera_info()
        if not cam_info:
            print("[Camera]  Ensure the camera is connected and enabled.")
            return
        picam2 = Picamera2()
        # Configure camera for video
        config = picam2.create_video_configuration(
            main={"size": (CAM_WIDTH, CAM_HEIGHT), "format": "RGB888"},
            controls={
                "FrameDurationLimits": (int(1e6 / CAM_FPS), int(1e6 / CAM_FPS))
            }
        )
        picam2.configure(config)
        picam2.start()
        print("[Camera] Camera started successfully.")
    except Exception as e:
        print(f"[Camera] Failed to initialize camera: {e}")
        return
    
    sleep_dt = 1.0 / CAM_FPS if CAM_FPS > 0 else 0.05

    while True:
        await asyncio.sleep(sleep_dt)

        # Capture frame from PiCam
        frame = picam2.capture_array()
        


        if frame is None or frame.size == 0:
            await asyncio.sleep(0.1)
            continue

        # Apply night vision enhancement if enabled
        if globals.night_vision:
            if globals.reset_cam_config:
                globals.brightness = globals.BRIGHTNESS
                globals.contrast = globals.CONTRAST
                globals.gamma_val = globals.GAMMA_VAL
                globals.reset_cam_config = False
                globals.cam_mode = 1

            frame = enhance.enhance_frame(
                frame,
                mode=globals.cam_mode,
                brightness=globals.brightness,
                contrast=globals.contrast,
                gamma_val=globals.gamma_val
            )
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Encode to JPEG
        ret_enc, buffer = cv2.imencode(".jpg", frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        if not ret_enc:
            continue
        frame_bytes = buffer.tobytes()

        # Send to WebSocket video clients
        if video_clients:
            await asyncio.gather(*[
                ws.send(frame_bytes) for ws in list(video_clients)
            ])

        # Send to raw socket clients (if enabled)
        if socket_clients and RUN_SOCKET_SERVER:
            for client in list(socket_clients):
                try:
                    client.write(len(frame_bytes).to_bytes(4, byteorder='big') + frame_bytes)
                    await client.drain()
                except Exception as e:
                    print(f"[Raw Socket] Failed to send to client: {e}")
                    socket_clients.remove(client)