# quick_test_full_on.py
import RPi.GPIO as GPIO
import time

LEFT_PWM, LEFT_IN1, LEFT_IN2 = 12, 23, 24
RIGHT_PWM, RIGHT_IN1, RIGHT_IN2 = 13, 8, 7

GPIO.setmode(GPIO.BCM)
GPIO.setup([LEFT_IN1, LEFT_IN2, RIGHT_IN1, RIGHT_IN2], GPIO.OUT)
GPIO.setup([LEFT_PWM, RIGHT_PWM], GPIO.OUT)

p_left = GPIO.PWM(LEFT_PWM, 200)   # 200 Hz for testing
p_right = GPIO.PWM(RIGHT_PWM, 200)
p_left.start(0)
p_right.start(0)

try:
    # Force left forward, right forward at full duty
    GPIO.output(LEFT_IN1, GPIO.HIGH)
    GPIO.output(LEFT_IN2, GPIO.LOW)
    GPIO.output(RIGHT_IN1, GPIO.HIGH)
    GPIO.output(RIGHT_IN2, GPIO.LOW)

    p_left.ChangeDutyCycle(100)
    p_right.ChangeDutyCycle(100)

    print("Set PWM to 100% for 5 s - measure motor terminals now.")
    time.sleep(5)

finally:
    p_left.stop()
    p_right.stop()
    GPIO.cleanup()