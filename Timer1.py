# Main program file
import RPi.GPIO as GPIO
import time

BUTTON = 13
is_Timer_Running = False
start_Time = 0

#for button
DOUBLE_PRESS_WINDOW = 0.5  #seconds to wait for a second press

press_count = 0
last_time_pressed = 0

def button_callback(channel): #callback function for what it should do when pressed
    global press_count, last_time_pressed
    press_count += 1
    last_time_pressed = time.time()

def setup():
    #setup GPIO board pins
    GPIO.setmode(GPIO.BOARD)

    #button
    GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #remember presses even while the program is busy doing something else
    GPIO.add_event_detect(BUTTON, GPIO.FALLING, callback=button_callback, bouncetime=200)

def check():
    #returns 0 (not pressed), 1 (pressed once) or 2 (pressed twice)
    global press_count
    if press_count == 0:
        return 0
    if time.time() - last_time_pressed < DOUBLE_PRESS_WINDOW:
        return 0 #still 0 waiting if second press comes
    presses = min(press_count, 2)
    press_count = 0
    return presses


def loop():
    #MAIN PROGRAM LOOP
    while True:
        global is_Timer_Running, start_Time
        presses = check()
        if presses == 1:
            print(f"Pressed {presses} time(s)")
        if presses == 2:
            if(not is_Timer_Running):
                start_Time = time.time()
                is_Timer_Running = True
                print("Timer started")
            elif(is_Timer_Running):
                print(f"current timer time is {time.time() - start_Time}")

        time.sleep(0.05)
        


def destroy():
    GPIO.cleanup()

if __name__ == "__main__":
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()