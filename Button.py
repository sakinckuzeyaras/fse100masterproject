
# push button
import RPi.GPIO as GPIO
import time

BUTTON = 13
DOUBLE_PRESS_WINDOW = 0.5  #seconds to wait for a second press

press_count = 0;
last_time_pressed = 0;

def button_callback(channel): #callback function for what it should do when pressed
    global press_count, last_time_pressed
    press_count += 1
    last_time_pressed = time.time()


def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #remember presses even while the program is busy doing something else
    GPIO.add_event_detect(BUTTON, GPIO.FALLING, callback=button_callback, bouncetime=200)

def check():
    #returns 0 (not pressed), 1 (pressed once) or 2 (pressed twice)
    global press_count
    if press_count == 0:
        return 0
    if time.time() - last_pressed_time < DOUBLE_PRESS_WINDOW:
        return 0 #still 0 waiting if second press comes
    presses = min(press_count, 2)
    press_count = 0
    return presses

if __name__ == "__main__":
    setup()
    try:
        while True:
            presses = check()
            if presses:
                print(f"Pressed {presses} time(s)")
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
