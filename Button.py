
# push button
import RPi.GPIO as GPIO
import time

BUTTON = 13
DOUBLE_PRESS_WINDOW = 0.5  #seconds to wait for a second press


def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #remember presses even while the program is busy doing something else
    GPIO.add_event_detect(BUTTON, GPIO.FALLING, bouncetime=200)

def check():
    #returns 0 (not pressed), 1 (pressed once) or 2 (pressed twice)
    if not GPIO.event_detected(BUTTON):
        return 0
    time.sleep(DOUBLE_PRESS_WINDOW)
    if GPIO.event_detected(BUTTON):
        return 2
    return 1

if __name__ == "__main__":
    setup()
    try:
        while True:
            presses = check()
            if presses:
                print(f"Pressed {presses} time(s)")
            time.sleep(0.05)
    finally:
        GPIO.cleanup()
