"""
last edited : 28/08/2025
motor_control.py
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
    from controllers.motor_control import set_motor_command, cleanup
"""

import RPi.GPIO as GPIO
from config import PWM_FREQ, MEASURED_MAX_WHEEL_SPEED, FALLBACK_MAX_WHEEL_SPEED, MIN_START_DUTY

# Keep the same pins you provided
LEFT_PWM, LEFT_IN1, LEFT_IN2 = 12, 23, 24
RIGHT_PWM, RIGHT_IN1, RIGHT_IN2 = 13, 8, 7

GPIO.setmode(GPIO.BCM)
GPIO.setup([LEFT_IN1, LEFT_IN2, RIGHT_IN1, RIGHT_IN2], GPIO.OUT)
GPIO.setup([LEFT_PWM, RIGHT_PWM], GPIO.OUT)

# PWM setup
pwm_left = GPIO.PWM(LEFT_PWM, PWM_FREQ)
pwm_right = GPIO.PWM(RIGHT_PWM, PWM_FREQ)
pwm_left.start(0)
pwm_right.start(0)

def _get_max_wheel_speed():
    """Return measured max wheel speed or fallback if not set."""
    if MEASURED_MAX_WHEEL_SPEED is not None:
        return MEASURED_MAX_WHEEL_SPEED
    return FALLBACK_MAX_WHEEL_SPEED

def set_motor_command(v_l, v_r):
    """
    v_l, v_r : wheel angular velocities in rad/s (positive = forward)
    Converts to PWM duty cycles with minimum start duty and debug prints.
    """
    max_w = _get_max_wheel_speed()
    # Map angular velocity magnitude to duty % (0..100)
    duty_l = min(abs(v_l) / max_w * 100.0, 100.0) if max_w > 0 else 0.0
    duty_r = min(abs(v_r) / max_w * 100.0, 100.0) if max_w > 0 else 0.0

    # Apply minimum starting duty if nonzero (prevents buzzing)
    if duty_l > 0 and duty_l < MIN_START_DUTY:
        duty_l = MIN_START_DUTY
    if duty_r > 0 and duty_r < MIN_START_DUTY:
        duty_r = MIN_START_DUTY

    # Direction logic (assuming IN1 HIGH, IN2 LOW => forward)
    if v_l >= 0:
        GPIO.output(LEFT_IN1, GPIO.HIGH)
        GPIO.output(LEFT_IN2, GPIO.LOW)
    else:
        GPIO.output(LEFT_IN1, GPIO.LOW)
        GPIO.output(LEFT_IN2, GPIO.HIGH)

    if v_r >= 0:
        GPIO.output(RIGHT_IN1, GPIO.HIGH)
        GPIO.output(RIGHT_IN2, GPIO.LOW)
    else:
        GPIO.output(RIGHT_IN1, GPIO.LOW)
        GPIO.output(RIGHT_IN2, GPIO.HIGH)

    pwm_left.ChangeDutyCycle(duty_l)
    pwm_right.ChangeDutyCycle(duty_r)

    # Debug print (helpful while testing)
    print(f"[MOTOR] v_l={v_l:.2f} rad/s v_r={v_r:.2f} rad/s -> duty_l={duty_l:.1f}% duty_r={duty_r:.1f}%")

def cleanup():
    """Stop PWM and clean up GPIO. Safe to call multiple times."""
    try:
        pwm_left.stop()
        pwm_right.stop()
    except Exception:
        pass
    GPIO.cleanup()