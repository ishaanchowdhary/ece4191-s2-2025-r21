"""
servo_control.py
--------------------
Provides function to set IR GPIO logic input to low (OFF) or high (ON)

"""
import RPi.GPIO as GPIO
from config import *
import time

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Create a software PWM instance at 50Hz
servo_pwm = GPIO.PWM(SERVO_PIN, 50)
servo_pwm.start(0)  # initial duty 0


# The MGM90S typically expects:
# 0°  -> ~2.5% duty
# 90° -> ~7.5% duty
# 180°-> ~12.5% duty
# You can adjust these below for calibration.
DUTY_DOWN = 2.5     # Servo fully down
DUTY_REHOME = 7.5   # Center (straight ahead)
DUTY_UP = 12.0      # Servo fully up

def set_servo_position(duty):
    """Move the servo to a specific position via software PWM."""
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)  # give servo time to reach position
    servo_pwm.ChangeDutyCycle(0)  # stop sending pulses to reduce jitter

def servo_up():
    """Rotate servo to UP position."""
    set_servo_position(DUTY_UP)
    print("Servo moved UP")

def servo_down():
    """Rotate servo to DOWN position."""
    set_servo_position(DUTY_DOWN)
    print("Servo moved DOWN")

def servo_rehome():
    """Rehome servo to neutral (straight ahead) position."""
    set_servo_position(DUTY_REHOME)
    print("Servo rehomed (centered)")

def cleanup():
    """Stop PWM safely."""
    servo_pwm.stop()
    # Leave GPIO cleanup to global motor control cleanup
    print("Servo cleanup complete")