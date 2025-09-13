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
import threading, time, math
from config import PWM_FREQ, MEASURED_MAX_WHEEL_SPEED, FALLBACK_MAX_WHEEL_SPEED, MIN_START_DUTY
from .velocity_smoother import tanh_ramp
# Pins
LEFT_PWM, LEFT_IN1, LEFT_IN2 = 12, 23, 24
RIGHT_PWM, RIGHT_IN1, RIGHT_IN2 = 13, 8, 7

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup([LEFT_IN1, LEFT_IN2, RIGHT_IN1, RIGHT_IN2], GPIO.OUT)
GPIO.setup([LEFT_PWM, RIGHT_PWM], GPIO.OUT)

# PWM setup
pwm_left = GPIO.PWM(LEFT_PWM, PWM_FREQ)
pwm_right = GPIO.PWM(RIGHT_PWM, PWM_FREQ)
pwm_left.start(0)
pwm_right.start(0)
# === State variables ===
current_duty_l = 0.0
current_duty_r = 0.0
target_duty_l = 0.0
target_duty_r = 0.0

# Ramp parameters
RAMP_TIME = 2      # seconds to go from 0→100%
UPDATE_HZ = 50       # update loop frequency
running = True




def _get_max_wheel_speed():
    """Return measured max wheel speed or fallback if not set."""
    if MEASURED_MAX_WHEEL_SPEED is not None:
        return MEASURED_MAX_WHEEL_SPEED
    return FALLBACK_MAX_WHEEL_SPEED

def set_motor_command(direction_l, direction_r, duty_l=100, duty_r=100):
    """
    feed the direction commands for left and right motors. 1 = forward, -1 = backward, 0 = stop
    Converts to PWM duty cycles with minimum start duty and debug prints.
    """

    global target_duty_l, target_duty_r
    target_duty_l = max(0, min(100, duty_l))
    target_duty_r = max(0, min(100, duty_r))


    # Direction logic (assuming IN1 HIGH, IN2 LOW => forward)
    if direction_l == -1:
        GPIO.output(LEFT_IN1, GPIO.HIGH) # left backward
        GPIO.output(LEFT_IN2, GPIO.LOW)
    elif direction_l == 1:
        GPIO.output(LEFT_IN1, GPIO.LOW) # left forward
        GPIO.output(LEFT_IN2, GPIO.HIGH)
    else:
        GPIO.output(LEFT_IN1, GPIO.LOW) # left stop
        GPIO.output(LEFT_IN2, GPIO.LOW)

    if direction_r == -1:
        GPIO.output(RIGHT_IN1, GPIO.HIGH)   # right backward
        GPIO.output(RIGHT_IN2, GPIO.LOW)
    elif direction_r == 1:
        GPIO.output(RIGHT_IN1, GPIO.LOW) # right forward
        GPIO.output(RIGHT_IN2, GPIO.HIGH)
    else:
        GPIO.output(RIGHT_IN1, GPIO.LOW) # right stop
        GPIO.output(RIGHT_IN2, GPIO.LOW)

    # Return duty cycles for testing/verification
    return duty_l, duty_r

    # Debug print (helpful while testing)
    print(f"[MOTOR] v_l={v_l:.2f} rad/s v_r={v_r:.2f} rad/s -> duty_l={duty_l:.1f}% duty_r={duty_r:.1f}%")



def pwm_update_loop():
    """Background thread: ramps duty toward target with tanh smoothing."""
    global current_duty_l, current_duty_r
    step_time = 1.0 / UPDATE_HZ
    last_target_l = target_duty_l
    last_target_r = target_duty_r
    ramp_start_l = current_duty_l
    ramp_start_r = current_duty_r
    elapsed = 0.0

    while running:
        print(current_duty_l)
        # If target changed, restart ramp
        if target_duty_l != last_target_l:
            ramp_start_l = current_duty_l
            elapsed = 0.0
            last_target_l = target_duty_l
        if target_duty_r != last_target_r:
            ramp_start_r = current_duty_r
            elapsed = 0.0
            last_target_r = target_duty_r

        # Update duty based on tanh easing
        elapsed += step_time
        elapsed = min(elapsed, RAMP_TIME)

        current_duty_l = tanh_ramp(ramp_start_l, target_duty_l, elapsed, RAMP_TIME)
        current_duty_r = tanh_ramp(ramp_start_r, target_duty_r, elapsed, RAMP_TIME)

        pwm_left.ChangeDutyCycle(current_duty_l)
        pwm_right.ChangeDutyCycle(current_duty_r)

        time.sleep(step_time)

threading.Thread(target=pwm_update_loop, daemon=True).start()


def cleanup():
    """Stop PWM and clean up GPIO. Safe to call multiple times."""
    global running, pwm_left, pwm_right
    running = False
    time.sleep(1.0 / UPDATE_HZ)  # let thread exit
    try:
        pwm_left.stop()
        pwm_right.stop()
        pwm_left = None
        pwm_right = None
        GPIO.cleanup()
        print("GPIO cleanup done.")
    except Exception as e:
        print("Error during GPIO cleanup:", e)