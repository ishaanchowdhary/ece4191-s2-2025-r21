"""
last edited : 28/08/2025
config.py
----------
Configuration constants
----------

- WebSocket server ports for command and video streaming
- Physical parameters (wheelbase, wheel radius)
- Motor PWM configuration and tuning parameters

Usage:
    from config import CMD_PORT, VIDEO_PORT, WHEEL_BASE, WHEEL_RADIUS
"""

# Networking
CMD_PORT = 9000
VIDEO_PORT = 9001

# Physics / geometry (used to convert v,w -> wheel velocities)
WHEEL_BASE = 0.15   # meters (L)
WHEEL_RADIUS = 0.065  # meters (R)

# PWM & motor tuning
PWM_FREQ = 50  # Hz
MEASURED_MAX_WHEEL_SPEED = None  # rad/s, set measured value if available
FALLBACK_MAX_WHEEL_SPEED = 40.0   # rad/s — conservative starting point
MIN_START_DUTY = 100.0             # percent, minimum duty to reliably start motor

# Camera defaults (used by camera_stream)
CAM_INDEX = 0
CAM_WIDTH = 640
CAM_HEIGHT = 480
CAM_FPS = 60