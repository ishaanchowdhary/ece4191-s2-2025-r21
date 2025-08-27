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