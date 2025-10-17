"""
servo_control.py
--------------------
Provides function to set IR GPIO logic input to low (OFF) or high (ON)

"""
import RPi.GPIO as GPIO
from config import *
import time

# =========================================================
# GPIO and PWM setup
# =========================================================
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Create software PWM at 50Hz
servo_pwm = GPIO.PWM(SERVO_PIN, 50)
servo_pwm.start(0)

# =========================================================
# Servo duty cycle configuration
# =========================================================
DUTY_MIN = 2.5     # physical lower limit (~0°)
DUTY_MAX = 12.5    # physical upper limit (~180°)
DUTY_REHOME = 7.5  # center (~90°)
STEP = 0.5         # size of each small movement (adjust as needed)

# Keep track of current servo duty
current_duty = DUTY_REHOME

# =========================================================
# Helper functions
# =========================================================
def set_servo_position(duty):
    """Low-level helper to move the servo to a specific duty cycle."""
    global current_duty
    # Clamp within physical range
    duty = max(DUTY_MIN, min(DUTY_MAX, duty))
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.4)
    servo_pwm.ChangeDutyCycle(0)
    current_duty = duty

# =========================================================
# Public functions
# =========================================================
def servo_up():
    """Move the servo slightly upward."""
    global current_duty
    new_duty = current_duty + STEP
    set_servo_position(new_duty)
    print(f"Servo nudged UP (duty={new_duty:.2f}%)")

def servo_down():
    """Move the servo slightly downward."""
    global current_duty
    new_duty = current_duty - STEP
    set_servo_position(new_duty)
    print(f"Servo nudged DOWN (duty={new_duty:.2f}%)")

def servo_rehome():
    """Rehome servo to center (straight ahead)."""
    set_servo_position(DUTY_REHOME)
    print("Servo rehomed (centered)")

def cleanup():
    """Stop PWM safely."""
    servo_pwm.stop()
    print("Servo cleanup complete")