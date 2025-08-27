"""
last edited : 28/08/2025
velocity_smoother.py
----------------------
Implements velocity smoothing to prevent abrupt motor commands.
----------------------
- Gradually adjust linear and angular velocity commands based on max acceleration limits.
- Provide a method to compute smoothed velocity values each update cycle.

"""