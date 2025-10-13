"""
motor_control.py
----------------

This module handles:
- GPIO setup for motor driver control.
- Conversion of direction commands to PWM duty cycles.
- Smooth ramping of motor speeds using a tanh ramp.
- Logging of PWM activity to CSV.
- Safe cleanup of GPIO and PWM on exit.

Main Functions:
- set_motor_command(direction_l, direction_r)
    Set left and right motor directions: 1 = forward, -1 = backward, 0 = stop.

- cleanup()
    Stop PWM outputs and clean up GPIO pins safely.

Background Thread:
- pwm_update_loop(min_duty, max_duty)
    Continuously ramps the PWM duty cycle towards the target value to prevent abrupt changes.

Dependencies:
- RPi.GPIO: Access to GPIO pins.
- config.py: Motor constants, PWM frequency, ramp time.
- globals.py: Global variables including min/max duty and logging flag.
- velocity_smoother.py: Provides tanh_ramp function for smooth duty cycle transitions.
"""


import RPi.GPIO as GPIO
import threading, time
from config import *
from .velocity_smoother import tanh_ramp
import csv
import math
import globals

# ------- CSV Logging setup -------
path = "pwm_log.csv"
# Open CSV and write header
log_fh = open(path, "w", newline="")
csv_writer = csv.writer(log_fh)
csv_writer.writerow(["timestamp", "current_duty", "target_duty", "min_duty"])

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



def set_motor_command(direction_l, direction_r):
    """
    feed the direction commands for left and right motors. 1 = forward, -1 = backward, 0 = stop
    Converts to PWM duty cycles with minimum start duty and debug prints.
    """
    global target_duty

    # If both directions are 0, set target duty to 0 (stop)
    if direction_l == 0 and direction_r == 0:
        target_duty = 0
    # If either direction is non-zero, set target duty to max_duty
    else:
        target_duty = globals.max_duty 


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
- The motors operate in a loop, with PWM values calculated with a tanh ramp function.
  Upon a change in target duty, the ramp resets.
"""
def pwm_update_loop():
    global current_duty, target_duty, prev_target_duty
    step_time = 1.0 / UPDATE_HZ
    elapsed = 0.0
    ramp_start_duty = current_duty

    while running:
        # Check if the target duty has changed. If so, reset ramp parameters.
        if target_duty != prev_target_duty:
            elapsed = 0.0
            ramp_start_duty = current_duty
            prev_target_duty = target_duty

        # Compute smoothed duty based on elapsed time in ramp
        current_duty = tanh_ramp(
            ramp_start_duty,
            target_duty,
            elapsed,
            RAMP_TIME
        )

        # Apply correction factors
        corrected_left_duty = current_duty * LEFT_CORRECTION
        corrected_right_duty = current_duty * RIGHT_CORRECTION

        # Clamp to valid range (0–100)
        corrected_left_duty = max(0, min(100, corrected_left_duty))
        corrected_right_duty = max(0, min(100, corrected_right_duty))

        pwm_left.ChangeDutyCycle(corrected_left_duty)
        pwm_right.ChangeDutyCycle(corrected_right_duty)
        # Log for debugging
        if LOGGING:
            timestamp = time.time()
            csv_writer.writerow([timestamp, corrected_left_duty, corrected_right_duty, target_duty, globals.min_duty])
            log_fh.flush()
        print(duty_to_velocity(corrected_left_duty))
        # Increment elapsed time
        elapsed += step_time
        if elapsed > RAMP_TIME:
            elapsed = RAMP_TIME  # clamp at end of ramp

        time.sleep(step_time)
threading.Thread(target=pwm_update_loop, daemon=True).start()


def duty_to_velocity(duty):
    """Convert PWM duty cycle to linear velocity (m/s) using wheel radius."""
    # For PWM frequency of 1kHz
    if duty <= 31: 
        return 0.0
    a = -0.0000334276
    b = 0.0055758
    c = -0.125407

    
    # calculated function here
    return a*math.pow(duty,2)+b*duty+c

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