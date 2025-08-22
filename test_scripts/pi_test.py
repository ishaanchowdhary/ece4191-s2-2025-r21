# This Python script will be used for testing connectivity with the client GUI

import asyncio
import json
import websockets


# --- Settings ---
WS_PORT = 9000

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

                    # Send acknowledgement
                    await websocket.send(json.dumps({
                        "status": "YIPPE",
                        "command": action,
                        "velocities": {"left": "v_l", "right": "v_r"}
                    }))

                else:
                    print("Unknown command:", action)
                    await websocket.send(json.dumps({"status": "error", "msg": "Invalid command"}))

            except json.JSONDecodeError:
                print("Invalid JSON received")
                await websocket.send(json.dumps({"status": "error", "msg": "Bad JSON"}))

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")


async def main():
    async with websockets.serve(handle_client, "0.0.0.0", WS_PORT):
        print(f"WebSocket server running on port {WS_PORT}")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")