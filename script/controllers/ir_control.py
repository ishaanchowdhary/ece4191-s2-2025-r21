"""
ir_control.py
--------------------
Provides function to set IR GPIO logic input to low (OFF) or high (ON)

"""
import RPi.GPIO as GPIO
from config import *

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(IR_PIN, GPIO.OUT)
GPIO.output(IR_PIN, GPIO.LOW)  # default to off

def ir_on():
    """Turn on IR LED"""
    GPIO.output(IR_PIN, GPIO.HIGH)
    print("IR LED ON")

def ir_off():
    """Turn off IR LED"""
    GPIO.output(IR_PIN, GPIO.LOW)
    print("IR LED OFF")

def cleanup():
    """Cleanup"""
    GPIO.output(IR_PIN, GPIO.LOW) # Turn off
    #GPIO.cleanup() #commenting out because motor control cleanup function already calls this