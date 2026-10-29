#Test for timer implementation with main code

import RPi.GPIO as GPIO
import time
import os
import subprocess

TRIG = 11
ECHO = 12
BUTTON1 = 15
BUTTON2 = 33
VIBRATION_MOTOR = 16

is_Timer_Running = False
start_Time = 0

press_count = 0
last_time_pressed = 0

rare_flag = False
mediumrare_flag = False
medium_flag = False
mediumwell_flag = False
welldone_flag = False

#for button
DOUBLE_PRESS_WINDOW = 0.5  #seconds to wait for a second press

ds18b20 = ''

#vibration motor
GPIO.setmode(GPIO.BOARD)
GPIO.setup(VIBRATION_MOTOR, GPIO.OUT)
motor_pwm = GPIO.PWM(VIBRATION_MOTOR, 100)

def setup():
    #setup GPIO board pins
    GPIO.setmode(GPIO.BOARD)

    #ultrasonic sensor
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

    #button1
    GPIO.setup(BUTTON1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #remember presses even while the program is busy doing something else
    GPIO.add_event_detect(BUTTON1, GPIO.FALLING, bouncetime=200)

    #button2
    GPIO.setup(BUTTON2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #remember presses even while the program is busy doing something else
    GPIO.add_event_detect(BUTTON2, GPIO.FALLING, bouncetime=200)
    
    #temp sensor
    global ds18b20
    for i in os.listdir('/sys/bus/w1/devices'):
        if i != 'w1_bus_master1':
            ds18b20 = '28-092250355fc8'

    

def distance():
    #measure and return ultrasonic sensor distance
    GPIO.output(TRIG, 0)
    time.sleep(0.000002)
    GPIO.output(TRIG, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG, 0)

    while GPIO.input(ECHO) == 0:
        pass
    time1 = time.time()
    while GPIO.input(ECHO) == 1:
        pass
    time2 = time.time()

    duration = time2 - time1
    return (duration * 340 / 2) * 100 #convert to and return in centimeters

def vibrate_for_seconds(seconds=0.5):
    #activates vibration motor for a specified number of seconds
    GPIO.output(VIBRATION_MOTOR, GPIO.HIGH)
    time.sleep(seconds)
    GPIO.output(VIBRATION_MOTOR, GPIO.LOW)
    time.sleep(seconds)

def vibrate_at_power(power = 30):
    #Set vibration motor to certain power
    motor_pwm.start(0)
    motor_pwm.ChangeDutyCycle(power)

def stop_pwm_vibration():
    #MUST be called before using vibrate_for_seconds
    motor_pwm.stop()

def read():
    #global ds18b20
    location = '/sys/bus/w1/devices/' + ds18b20 + '/w1_slave'
    tfile = open(location)
    text = tfile.read()
    tfile.close()
    secondline = text.split("\n")[1]
    temperaturedata = secondline.split(" ")[9]
    temperature = float(temperaturedata[2:])
    temperature = temperature / 1000
    return temperature

def check_button1(): #button for temperature, any presses gives current temp
    #returns 0 (not pressed), 1 (pressed once) or 2 (pressed twice)
    if not GPIO.event_detected(BUTTON1):
        return 0
    time.sleep(DOUBLE_PRESS_WINDOW)
    if GPIO.event_detected(BUTTON1):
        return 2
    return 1

def check_button2(): #button for temperature, any presses gives current temp
    #returns 0 (not pressed), 1 (pressed once) or 2 (pressed twice)
    if not GPIO.event_detected(BUTTON2):
        return 0
    time.sleep(DOUBLE_PRESS_WINDOW)
    if GPIO.event_detected(BUTTON2):
        return 2
    return 1

def speak(text):
    subprocess.run(["espeak", text])

def timerCheck():
    global rare_flag, mediumrare_flag, medium_flag, mediumwell_flag, welldone_flag
    if(is_Timer_Running):
        timerTime = time.time() - start_Time
        if timerTime > 10: #180
            if rare_flag == False:
                speak("Meat is now Rare, Flip and reset timer")
                rare_flag = True
        if timerTime > 20: #240
            if mediumrare_flag == False:
                speak("Meat is now Medium Rare, Flip and reset timer")
                mediumrare_flag = True
        if timerTime > 300:
            if medium_flag == False:
                speak("Meat is now Medium, Flip and reset timer")
                medium_flag = True
        if timerTime > 360:
            if mediumwell_flag == False:
                speak("Meat is now Medium Well, Flip and reset timer")
                mediumwell_flag = True
        if timerTime > 400:
            if welldone_flag == False:
                speak("Meat is now Well Done, Flip and reset timer")
                welldone_flag = True

def loop():
    #MAIN PROGRAM LOOP
    global is_Timer_Running, start_Time
    global rare_flag, mediumrare_flag, medium_flag, mediumwell_flag, welldone_flag

    while True:
        dis = distance()
        print(f"Object detected at: {dis} cm")

        if dis < 20: #distance less than 20 cm
            temp = read()
            if(temp >= 43): #43): #according to google, 43 degrees C is when something begins to be "too hot to touch"
                stop_pwm_vibration()
                seconds = 30/temp #higher the temp means more requent the buzzes
                vibrate_for_seconds(seconds)
            #Once temperature sensor is implemented, have an if statement first to check temperature,
            #temperature vibrations take priority to distance vibrations
            else:
                vibrate_at_power(30) #change once confirm this works
        else:
            vibrate_at_power(0)
            stop_pwm_vibration()

        timerCheck()

        presses1 = check_button1()
        if presses1:
            if read() != None:
                if(not is_Timer_Running):
                    start_Time = time.time()
                    is_Timer_Running = True
                    speak("Timer started")
                elif(is_Timer_Running):
                    start_Time = 0
                    is_Timer_Running = False
                    speak("Timer stopped")
                    rare_flag = True
                    mediumrare_flag = True
                    medium_flag = True
                    mediumwell_flag = True
                    welldone_flag = True

        presses2 = check_button2()
        if presses2:
            if read() != None:
                temp = read()
                print ("Current temperature : %0.3f C" % temp)
                speak_message = f"Current Temperature is {temp:.2f} degrees Celsius."
                speak(speak_message)
        time.sleep(0.05)
        


def destroy():
    motor_pwm.stop()
    GPIO.cleanup()

if __name__ == "__main__":
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()