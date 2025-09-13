"""
velocity_smoother.py
--------------------
Provides functions to smoothly ramp motor PWM duty cycles using a hyperbolic tangent (tanh) function.

This module is used by the motor control system to:
- Gradually adjust motor speeds to avoid abrupt starts or stops.
- Ensure a minimum duty cycle is applied to overcome motor deadzone.
- Smoothly transition between target PWM values over a specified ramp time.

Main Functions:
- tanh_ramp(start, target, elapsed, total_time)
    Computes a smooth PWM duty cycle based on a tanh curve from start to target.
    Ensures minimum duty cycle is applied if target is non-zero and clamps values for safety.

Dependencies:
- math: For tanh function calculation.
- globals: For global min_duty used to handle motor deadzone.
"""

import math
import globals


def tanh_ramp(start, target, elapsed, total_time):
    """
    Smooth tanh ramp from start to target, ensuring that
    if starting from 0, it begins at min_duty.
    """
    # Fetch min_duty from globals
    min_duty = globals.min_duty
    # If the target is non-zero and start is below min_duty, set start to min_duty. This avoids entering the ramp midway.
    if start < min_duty and target != 0:
        start = min_duty
    tuning_param = 7.6 # tuning parameter for steepness of tanh curve
    # Calculate duty cycle using tanh function
    duty = start + ((target - start)/2) * (math.tanh((tuning_param/total_time)*(elapsed - total_time/2))+1)

    # Round large and small values
    if duty > 99.5:
        duty = 100
    elif duty < 0.05: 
        duty = 0.0

    # Minimum duty cycle to overcome motor deadzone
    if target != 0:
        if duty < min_duty:
            duty = min_duty
    elif target == 0:
        if duty < min_duty:
            duty = 0
    return duty


