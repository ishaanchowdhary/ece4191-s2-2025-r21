"""
globals.py
----------
Global variables

These variables are used across multiple modules to define PWM limits
as well as camera vision parameters and allow dynamic updates at run-
time (e.g., via WebSocket commands).

Variables:
- min_duty (int or float): Minimum PWM duty cycle applied to motors.
  Ensures motors overcome deadzone when starting from rest.
  Default: 40

- max_duty (int or float): Maximum PWM duty cycle applied to motors.
  Default: 100

- night_vision (Bool): Enables "night-vision" mode.
- reset_cam_config (Bool) Resets camera configuration to defaults.
- cam_mode (int): Switches between camera modes.
- brightness (int): Adjusts brightness camera param.
- contrast (int): Adjusts contrast camera param.
- gamma_val (int): Adjusts gamma camera param.
"""

# Minimum PWM duty cycle to overcome motor deadzone
min_duty = 40

# Maximum PWM duty cycle
max_duty = 100

# ---For camera vision---
night_vision = False
reset_cam_config = False
cam_mode = 1 # Default [0,4]
brightness = 50
contrast = 50
gamma_val = 300