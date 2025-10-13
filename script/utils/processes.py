import subprocess
import asyncio
import json 
import psutil
from config import *
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


async def send_velocity_periodically(websocket, interval=0.1):
    """Send current velocity to GUI at faster rate (default: 0.3 s)."""
    last_velocity = 0.0
    while True:
        if websocket.closed:
            break
        velocity = round(globals.current_velocity, 4)
        if last_velocity != 0.0:
            await websocket.send(json.dumps({"velocity_update": velocity}))
            last_velocity = velocity
        await asyncio.sleep(interval)