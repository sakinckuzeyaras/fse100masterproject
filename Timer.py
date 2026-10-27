# Main program file
import RPi.GPIO as GPIO
import time

BUTTON = 13
is_Timer_Running = False
press_Start_Time = 0

#for button
DOUBLE_PRESS_WINDOW = 0.5  #seconds to wait for a second press

def setup():
    #setup GPIO board pins
    GPIO.setmode(GPIO.BOARD)

    #button
    GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #remember presses even while the program is busy doing something else
    GPIO.add_event_detect(BUTTON, GPIO.FALLING, bouncetime=200)

def check():
    #returns 0 (not pressed), 1 (pressed once) or 2 (pressed twice)
    global press_Start_Time
    if not GPIO.event_detected(BUTTON):
        if(press_Start_Time != 0):    
            if((time.time() - press_Start_Time) > 1):
                press_Start_Time = 0
                return 1
            else:
                return 0
        else: 
            return 0
    if GPIO.event_detected(BUTTON):
        press_Current_Time = time.time()
        if(press_Start_Time == 0):
            press_Start_Time = time.time()
        else:
            if((press_Current_Time - press_Start_Time) <= 0.5):
                return 2


def loop():
    #MAIN PROGRAM LOOP
    while True:

        presses = check()
        if(presses == 1):
            print("1 press")
        elif(presses == 2):
            print("2 presses")
        


def destroy():
    GPIO.cleanup()

if __name__ == "__main__":
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()