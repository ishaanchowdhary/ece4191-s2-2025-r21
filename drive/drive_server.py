# Main script that reads in commands from websocket 
import asyncio
import json
import websockets
from motor_control import set_motor_command
from motor_control import cleanup  
from smoothing import VelocitySmoother

# --- Settings ---
WS_PORT = 9000

# Velocity smoother instance
smoother = VelocitySmoother(max_accel=0.5, max_ang_accel=1.0, rate_hz=50)

# Command mapping (adjust speeds as needed)
COMMAND_MAP = {
    "FORWARD":  {"v": 0.5, "w": 0.0},
    "REVERSE":  {"v": -0.5, "w": 0.0},
    "LEFT":     {"v": 0.0, "w": 0.8},
    "RIGHT":    {"v": 0.0, "w": -0.8},
    "STOP":     {"v": 0.0, "w": 0.0}
}

async def handle_client(websocket, path):
    print("Client connected")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                action = data.get("action", "").upper()

                if action in COMMAND_MAP:
                    target = COMMAND_MAP[action]

                    # Smooth velocities
                    v_smooth, w_smooth = smoother.update(target["v"], target["w"])

                    # Convert to wheel velocities
                    # Differential drive equations
                    L = 0.15  # wheelbase (m) - adjust!
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

                else:
                    print("Unknown command:", action)
                    await websocket.send(json.dumps({"status": "error", "msg": "Invalid command"}))

            except json.JSONDecodeError:
                print("Invalid JSON received")
                await websocket.send(json.dumps({"status": "error", "msg": "Bad JSON"}))

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
        set_motor_command(0, 0)  # stop motors on disconnect


async def main():
    async with websockets.serve(handle_client, "0.0.0.0", WS_PORT):
        print(f"WebSocket server running on port {WS_PORT}")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")
    finally:
        cleanup()