import subprocess
import asyncio
import json 
import psutil
from config import *
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

async def send_cpu_usage(websocket):
    """Send Pi status to the connected GUI every 10 seconds."""
    while True:
        if websocket.closed:
            break
        usage = psutil.cpu_percent(interval=CPU_USAGE_INTERVAL)
        print(usage)
        #await websocket.send(json.dumps({"status_update": status}))
        await asyncio.sleep(CPU_USAGE_INTERVAL)  # 10-second interval