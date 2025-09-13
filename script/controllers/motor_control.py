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
import threading, time
from config import *
from .velocity_smoother import tanh_ramp

import csv

LOG_FILE = "pwm_log.csv"  # adjust path as needed
# Open CSV and write header
log_fh = open(LOG_FILE, "w", newline="")
csv_writer = csv.writer(log_fh)
csv_writer.writerow(["timestamp", "current_duty", "target_duty"])

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
current_duty = 0.0
target_duty = 0.0
prev_target_duty = 0.0


running = True


def set_motor_command(direction_l, direction_r, duty):
    """
    feed the direction commands for left and right motors. 1 = forward, -1 = backward, 0 = stop
    Converts to PWM duty cycles with minimum start duty and debug prints.
    """
    global target_duty

    # Set new target duty cycles
    if direction_l == 0 and direction_r == 0:
        duty = 0
    target_duty = duty

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


"""
Background thread to smoothly update PWM duty cycle towards target.
"""
def pwm_update_loop():
    global current_duty, target_duty, prev_target_duty, MIN_START_DUTY
    step_time = 1.0 / UPDATE_HZ
    elapsed = 0.0
    ramp_start_duty = current_duty

    while running:
        # When there is a change in target duty cycle, reset ramp and set elapsed time to 0
        if target_duty != prev_target_duty:
            elapsed = 0.0
            ramp_start_duty = current_duty
            prev_target_duty = target_duty

        # Compute smoothed duty based on elapsed time in ramp
        current_duty = tanh_ramp(
            ramp_start_duty,
            target_duty,
            elapsed,
            RAMP_TIME,
            MIN_START_DUTY
        )

        # Apply PWM duty
        pwm_left.ChangeDutyCycle(current_duty)
        pwm_right.ChangeDutyCycle(current_duty)

        # Log for debugging
        if LOGGING:
            timestamp = time.time()
            csv_writer.writerow([timestamp, current_duty, target_duty])
            log_fh.flush()

        # Increment elapsed time
        elapsed += step_time
        if elapsed > RAMP_TIME:
            elapsed = RAMP_TIME  # clamp at end of ramp

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
        log_fh.close()
        print("GPIO cleanup done.")
    except Exception as e:
        print("Error during GPIO cleanup:", e)