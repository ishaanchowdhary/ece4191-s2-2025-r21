# motor_control.py (replace set_motor_command with this)
import RPi.GPIO as GPIO
import time

LEFT_PWM, LEFT_IN1, LEFT_IN2 = 12, 23, 24
RIGHT_PWM, RIGHT_IN1, RIGHT_IN2 = 13, 8, 7

GPIO.setmode(GPIO.BCM)
GPIO.setup([LEFT_IN1, LEFT_IN2, RIGHT_IN1, RIGHT_IN2], GPIO.OUT)
GPIO.setup([LEFT_PWM, RIGHT_PWM], GPIO.OUT)

# Try 200 Hz for brushed DC motors (adjust if needed)
PWM_FREQ = 200
pwm_left = GPIO.PWM(LEFT_PWM, PWM_FREQ)
pwm_right = GPIO.PWM(RIGHT_PWM, PWM_FREQ)
pwm_left.start(0)
pwm_right.start(0)

# TUNE THESE:
# MEASURED_MAX_WHEEL_SPEED (rad/s) = wheel angular speed at 100% PWM (no-load)
# If you haven't measured it yet, set a conservative default and then measure & update.
MEASURED_MAX_WHEEL_SPEED = None  # set to None to use fallback below
FALLBACK_MAX_WHEEL_SPEED = 20.0   # rad/s — conservative starting point
MIN_START_DUTY = 100.0             # minimum duty % to reliably start motor

def _get_max_wheel_speed():
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
    duty_l = min(abs(v_l) / max_w * 100.0, 100.0)
    duty_r = min(abs(v_r) / max_w * 100.0, 100.0)

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
    pwm_left.stop()
    pwm_right.stop()
    GPIO.cleanup()


""" # Script for motor control signals 
import RPi.GPIO as GPIO
import time

# GPIO pin setup
LEFT_PWM, LEFT_IN1, LEFT_IN2 = 12, 23, 24
RIGHT_PWM, RIGHT_IN1, RIGHT_IN2 = 13, 8, 7

GPIO.setmode(GPIO.BCM)
GPIO.setup([LEFT_IN1, LEFT_IN2, RIGHT_IN1, RIGHT_IN2], GPIO.OUT)
GPIO.setup([LEFT_PWM, RIGHT_PWM], GPIO.OUT)

pwm_left = GPIO.PWM(LEFT_PWM, 200)
pwm_right = GPIO.PWM(RIGHT_PWM, 200)
pwm_left.start(0)
pwm_right.start(0)

def set_motor_command(v_l, v_r):
    #Convert wheel velocity to PWM signals
    # Map velocities to duty cycle [-1,1] → [0,100]
    MAX_WHEEL_SPEED = 10.0  # TO TUNE 
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
    GPIO.cleanup() """