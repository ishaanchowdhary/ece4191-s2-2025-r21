"""
last edited : 28/08/2025
motor_controller.py
--------------------
Low-level motor control module for differential drive.
---------------------

- Configure GPIO pins for motor control.
- Convert wheel angular velocities (rad/s) to PWM duty cycles.
- Handle direction control for left and right motors.
- Provide cleanup function to safely stop motors and release GPIO.

Main Functions:
- set_motor_command(v_l, v_r): Apply motor speeds for left and right wheels.
- cleanup(): Stop PWM signals and reset GPIO state.

Dependencies:
- RPi.GPIO for hardware access
- config.py for motor constants and PWM settings

Usage:
    from controllers.motor_controller import set_motor_command, cleanup
"""