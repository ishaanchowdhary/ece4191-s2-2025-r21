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

import websockets

# Track connected video clients (module-level so camera_stream can import it)
video_clients = set()

async def handle_video(websocket, path):
    """Register client for video stream (keeps original signature)."""
    print("Video client connected")
    video_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        video_clients.remove(websocket)
        print("Video client disconnected")