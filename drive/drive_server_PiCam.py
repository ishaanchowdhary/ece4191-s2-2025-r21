# Main script that reads in commands from websocket and streams raw camera feed

import asyncio
import json
import websockets
from picamera2 import Picamera2
import cv2
from motor_control import set_motor_command, cleanup
from smoothing import VelocitySmoother

# --- Settings ---
CMD_PORT = 9000
VIDEO_PORT = 9001

# Init camera
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()


# Velocity smoother instance
smoother = VelocitySmoother(max_accel=0.5, max_ang_accel=2.0, rate_hz=50)

# Command mapping (adjust speeds as needed)
COMMAND_MAP = {
    "FORWARD":    {"v": 0.5, "w": 0.0},
    "REVERSE":    {"v": -0.5, "w": 0.0},
    "LEFT":       {"v": 0.0, "w": 0.8},
    "RIGHT":      {"v": 0.0, "w": -0.8},
    "DRIVE_STOP": {"v": 0.0, "w": 0.0}
}

# Track connected video clients
video_clients = set()

# ---------------- COMMAND SERVER ----------------
async def handle_client(websocket, path):
    print("Command client connected")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                action = data.get("action", "").upper()

                if action in COMMAND_MAP:
                    target = COMMAND_MAP[action]

                    # Smooth velocities
                    v_smooth, w_smooth = smoother.update(target["v"], target["w"])

                    # Differential drive equations
                    L = 0.15   # wheelbase (m) - adjust!
                    R = 0.065  # wheel radius (m) - adjust!
                    v_r = (2*v_smooth + w_smooth*L) / (2*R)
                    v_l = (2*v_smooth - w_smooth*L) / (2*R)

                    set_motor_command(v_l, v_r)

                    # Send acknowledgement
                    await websocket.send(json.dumps({
                        "status": "ok",
                        "command": action,
                        "velocities": {"left": v_l, "right": v_r}
                    }))

                    print(f"Command: {action} | v_l={v_l:.2f}, v_r={v_r:.2f}")

                else:
                    print("Unknown command:", action)
                    await websocket.send(json.dumps(
                        {"status": "error", "msg": "Invalid command"}
                    ))

            except json.JSONDecodeError:
                print("Invalid JSON received")
                await websocket.send(json.dumps(
                    {"status": "error", "msg": "Bad JSON"}
                ))

    except websockets.exceptions.ConnectionClosed:
        print("Command client disconnected")
        set_motor_command(0, 0)  # stop motors on disconnect


# ---------------- VIDEO SERVER ----------------
async def handle_video(websocket, path):
    """Register client for video stream"""
    print("Video client connected")
    video_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        video_clients.remove(websocket)
        print("Video client disconnected")

async def camera_stream():
    """Continuously capture and broadcast frames"""
    while True:
        await asyncio.sleep(0.05)  # ~20 FPS

        frame = picam2.capture_array()   # Get frame as numpy array
        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        if video_clients:
            await asyncio.gather(*[ws.send(frame_bytes) for ws in video_clients])



# ---------------- MAIN ----------------
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
    finally:
        set_motor_command(0, 0)  # safety stop
        cleanup()