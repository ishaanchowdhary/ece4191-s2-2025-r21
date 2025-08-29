#!/usr/bin/env python3
"""
last edited: 28/08/2025
main.py
--------
Entry point for the robot WebSocket control and video streaming system.
--------
- Start websocket servers
- Run camera stream
- Cleanup on shutdown

Usage:
    python3 main.py
"""

import asyncio
import websockets

from config import CMD_PORT, VIDEO_PORT
from servers.command_server import handle_client
from servers.video_server import handle_video
from servers.camera_stream import camera_stream
from controllers.motor_control import cleanup as motor_cleanup

async def main():
    # Start both servers
    await websockets.serve(handle_client, "0.0.0.0", CMD_PORT)
    await websockets.serve(handle_video, "0.0.0.0", VIDEO_PORT)

    print(f"Command WebSocket server on port {CMD_PORT}")
    print(f"Video WebSocket server on port {VIDEO_PORT}")

    # Run camera stream forever
    await camera_stream()


if __name__ == "__main__": 
    try:
        asyncio.run(main())                             
    except KeyboardInterrupt:
        print("Server stopped")
    finally: # Runs on exit
        motor_cleanup()