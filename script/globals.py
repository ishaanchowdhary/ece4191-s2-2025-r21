"""
globals.py
----------
Global variables

These variables are used across multiple modules to define PWM limits
and allow dynamic updates at runtime (e.g., via WebSocket commands).

Variables:
- min_duty (int or float): Minimum PWM duty cycle applied to motors.
  Ensures motors overcome deadzone when starting from rest.
  Default: 40

- max_duty (int or float): Maximum PWM duty cycle applied to motors.
  Default: 100
"""

# Minimum PWM duty cycle to overcome motor deadzone
min_duty = 40

# Maximum PWM duty cycle
max_duty = 100