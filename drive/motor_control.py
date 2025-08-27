# Script for motor control signals 
import RPi.GPIO as GPIO
import time

# GPIO pin setup
LEFT_PWM, LEFT_IN1, LEFT_IN2 = 12, 23, 24
RIGHT_PWM, RIGHT_IN1, RIGHT_IN2 = 13, 8, 7

GPIO.setmode(GPIO.BCM)
GPIO.setup([LEFT_IN1, LEFT_IN2, RIGHT_IN1, RIGHT_IN2], GPIO.OUT)
GPIO.setup([LEFT_PWM, RIGHT_PWM], GPIO.OUT)

pwm_left = GPIO.PWM(LEFT_PWM, 1000)
pwm_right = GPIO.PWM(RIGHT_PWM, 1000)
pwm_left.start(0)
pwm_right.start(0)

def set_motor_command(v_l, v_r):
    """Convert wheel velocity to PWM signals"""
    # Map velocities to duty cycle [-1,1] → [0,100]
    MAX_WHEEL_SPEED = 90.0  # TO TUNE 
    duty_l = min(abs(v_l) / MAX_WHEEL_SPEED * 100, 100)
    duty_r = min(abs(v_r) / MAX_WHEEL_SPEED * 100, 100)

    # Left motor direction
    if v_l >= 0:
        GPIO.output(LEFT_IN1, GPIO.HIGH)
        GPIO.output(LEFT_IN2, GPIO.LOW)
    else:
        GPIO.output(LEFT_IN1, GPIO.LOW)
        GPIO.output(LEFT_IN2, GPIO.HIGH)

    # Right motor direction
    if v_r >= 0:
        GPIO.output(RIGHT_IN1, GPIO.HIGH)
        GPIO.output(RIGHT_IN2, GPIO.LOW)
    else:
        GPIO.output(RIGHT_IN1, GPIO.LOW)
        GPIO.output(RIGHT_IN2, GPIO.HIGH)

    pwm_left.ChangeDutyCycle(duty_l)
    pwm_right.ChangeDutyCycle(duty_r)

def cleanup():
    pwm_left.stop()
    pwm_right.stop()
    GPIO.cleanup()