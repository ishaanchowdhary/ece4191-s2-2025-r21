"""
video_server.py
----------------
WebSocket server for registering video stream clients.

Responsibilities:
- Accept connections from clients interested in receiving camera frames.
- Maintain a set of active video clients for broadcasting.

Usage:
    await websockets.serve(handle_video, "0.0.0.0", VIDEO_PORT)
"""