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
SOCKET_PORT = 5002
RUN_SOCKET_SERVER = True

# Data logging
LOGGING = True
LOG_DIR = "logs"  # directory to save log files


# Physics / geometry (used to convert v,w -> wheel velocities)
WHEEL_BASE = 0.15   # meters (L)
WHEEL_RADIUS = 0.065  # meters (R)

# PWM & motor tuning
PWM_FREQ = 1000  # Hz
RAMP_TIME = 0.5      # seconds to go from 0 to 100%
UPDATE_HZ = 50       # update loop frequency
# Pins
LEFT_PWM, LEFT_IN1, LEFT_IN2 = 12, 23, 24
RIGHT_PWM, RIGHT_IN1, RIGHT_IN2 = 13, 8, 7

# Camera defaults (used by camera_stream)
CAM_INDEX = 0
CAM_WIDTH = 640
CAM_HEIGHT = 480
CAM_FPS = 30 #25
JPEG_QUALITY = 50