"""
safety.py
----------
Utility functions for emergency stop and safe system shutdown.

Responsibilities:
- Provide a global function to stop all actuators.
- Can be extended for watchdog timers or fault handling.

Usage:
    from utils.safety import emergency_stop
"""

from controllers.motor_controller import set_motor_command, cleanup as motor_cleanup

def emergency_stop():
    """Immediately stop motors (zero velocities) and perform cleanup."""
    try:
        set_motor_command(0, 0)
    except Exception:
        pass
    try:
        motor_cleanup()
    except Exception:
        pass