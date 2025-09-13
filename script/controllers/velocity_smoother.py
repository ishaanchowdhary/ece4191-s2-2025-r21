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

class VelocitySmoother:
    def __init__(self, max_accel=0.5, max_ang_accel=1.0, rate_hz=50):
        self.max_accel = max_accel
        self.max_ang_accel = max_ang_accel
        self.dt = 1.0 / rate_hz
        self.v_cur = 0.0
        self.w_cur = 0.0

    def update(self, v_target, w_target):
        # Linear velocity smoothing
        dv = v_target - self.v_cur
        max_dv = self.max_accel * self.dt
        if abs(dv) > max_dv:
            dv = max_dv if dv > 0 else -max_dv
        self.v_cur += dv

        # Angular velocity smoothing
        dw = w_target - self.w_cur
        max_dw = self.max_ang_accel * self.dt
        if abs(dw) > max_dw:
            dw = max_dw if dw > 0 else -max_dw
        self.w_cur += dw

        return self.v_cur, self.w_cur
    

def tanh_ramp(current, target, elapsed, total_time):
    """
    Return intermediate duty based on tanh easing.
    elapsed: seconds passed since start of ramp
    total_time: total ramp time
    """
    # Map elapsed to -1..+1
    x = (elapsed / total_time) * 2 - 1
    x = max(-1.0, min(1.0, x))
    # tanh curve 0..1
    y = (math.tanh(2.5 * x) + 1.0) / 2.0
    return current + (target - current) * y

