# temperature sensor
import RPi.GPIO as GPIO
import time

TRIG = 11
ECHO = 12
VIBRATION_MOTOR = 16


def setup():
    #setup GPIO board pins
    GPIO.setmode(GPIO.BOARD)

    #ultrasonic sensor
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

    #vibration motor
    GPIO.setup(VIBRATION_MOTOR, GPIO.OUT)

def vibrate_for_seconds(seconds=0.5):
    #activates vibration motor for a specified number of seconds
    GPIO.output(VIBRATION_MOTOR, GPIO.HIGH)
    time.sleep(seconds)
    GPIO.output(VIBRATION_MOTOR, GPIO.LOW)

def loop():
    #MAIN PROGRAM LOOP
    while True:
        print(f"")
        


def destroy():
    GPIO.cleanup()

if __name__ == "main":
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()