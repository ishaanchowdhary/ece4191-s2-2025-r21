import subprocess
import asyncio
import json 
import psutil
from config import *
import csv, time
import globals
def get_throttle_status():
    """Return Raspberry Pi under-voltage and throttled status."""
    try:
        output = subprocess.check_output(['vcgencmd', 'get_throttled']).decode()
        val = int(output.split('=')[1], 16)
        return {
            'under_voltage_now': bool(val & 0x1),
            'freq_capped_now': bool(val & 0x2),
            'throttled_now': bool(val & 0x4),
            'under_voltage_occurred': bool(val & 0x10000),
            'freq_capped_occurred': bool(val & 0x20000),
            'throttled_occurred': bool(val & 0x40000),
        }
    except Exception as e:
        return {"error": str(e)}


async def send_status_periodically(websocket):
    """Send Pi status to the connected GUI every 10 seconds."""
    while True:
        if websocket.closed:
            break
        status = get_throttle_status()
        await websocket.send(json.dumps({"status_update": status}))
        await asyncio.sleep(HEALTH_CHECK_INTERVAL)  # 10-second interval


async def send_velocity_periodically(websocket):
    """Send current velocity to GUI at faster rate ."""
    last_velocity = 0.0
    while True:
        if websocket.closed:
            break
        velocity = round(globals.current_velocity, 4)
        if last_velocity != 0.0:
            await websocket.send(json.dumps({"head": 'velocity_update', "vel":velocity, "l": globals.left_direction, "r":globals.right_direction}))
        last_velocity = velocity
        await asyncio.sleep(SEND_VELOCITY_INTERVAL)


CSV_FILE = "velocity_log.csv"
async def log_velocity_periodically(interval=0.005):
    """Log current velocity to a CSV file at a fixed interval (default 0.1s)."""
    cmd_path = "vel_log.csv"

    with open(cmd_path, "w", newline="") as log_fh:
        csv_writer = csv.writer(log_fh)
        csv_writer.writerow(["timestamp", "velocity", "left_direction", "right_direction"])
        log_fh.flush()

        while True:
            timestamp = time.perf_counter()
            velocity = round(globals.current_velocity, 4)

            csv_writer.writerow([
                timestamp,
                velocity,
                globals.left_direction,
                globals.right_direction
            ])

            log_fh.flush()  # ensure it's written immediately
            print(f"Logged velocity: {velocity}")
            await asyncio.sleep(interval)

async def handle_ping(websocket, data):
    """Handle ping messages from client to measure latency"""
    try:
        ts = data.get("timestamp")
        if ts is not None:
            await websocket.send(json.dumps({
                "action": "PONG",
                "timestamp": ts
            }))
        else:
            await websocket.send(json.dumps({
                "status": "error",
                "msg": "Missing timestamp in PING"
            }))
    except Exception as e:
        print(f"Error in handle_ping: {e}")