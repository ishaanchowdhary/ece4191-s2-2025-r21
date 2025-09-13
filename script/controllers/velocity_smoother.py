"""
last edited : 28/08/2025
velocity_smoother.py
----------------------
Implements velocity smoothing to prevent abrupt motor commands.
----------------------
- Gradually adjust linear and angular velocity commands based on max acceleration limits.
- Provide a method to compute smoothed velocity values each update cycle.

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


