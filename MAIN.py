#Test for timer implementation with main code

import RPi.GPIO as GPIO
import time
import os
import subprocess

TRIG = 11 #GPIO port 17
ECHO = 12 #GPIO port 18
BUTTON1 = 15 #GPIO 22
BUTTON2 = 33 #GPIO 13
VIBRATION_MOTOR = 16 #GPIO 23

#Global variables for timer, start time 0 by default, timer running check false by default
is_Timer_Running = False
start_Time = 0

press_count = 0
last_time_pressed = 0

#Various flags for determining if the time for each stage of rarity has passed already
rare_flag = False
mediumrare_flag = False
medium_flag = False
mediumwell_flag = False
welldone_flag = False

#for button (Somewhat redundant now since double clicks dont exist, but scared to remove just in case)
DOUBLE_PRESS_WINDOW = 0.5  #seconds to wait for a second press

#variable for temperature sensor address
ds18b20 = ''

#vibration motor
GPIO.setmode(GPIO.BOARD)
GPIO.setup(VIBRATION_MOTOR, GPIO.OUT)
#pwm for vibration motor allows 
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
    #ignores any signal within 200ms of pressing to avoid the button bouncing back up sending a signal

    #button2
    GPIO.setup(BUTTON2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #remember presses even while the program is busy doing something else
    GPIO.add_event_detect(BUTTON2, GPIO.FALLING, bouncetime=200)
     #ignores any signal within 200ms of pressing to avoid the button bouncing back up sending a signal
    
    #temp sensor setup
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

#This function is used for when the temperature exceeds a certain threshold, 
#buzzing the motor at full power for a set time interval
def vibrate_for_seconds(seconds=0.5):
    #activates vibration motor for a specified number of seconds
    GPIO.output(VIBRATION_MOTOR, GPIO.HIGH)
    time.sleep(seconds)
    GPIO.output(VIBRATION_MOTOR, GPIO.LOW)
    time.sleep(seconds)

#This function is for the low hum at given power when 
#distance is less than 20cm and temperature is not greater than 43 degrees Celsius
def vibrate_at_power(power = 30):
    #Set vibration motor to certain power
    motor_pwm.start(0)
    motor_pwm.ChangeDutyCycle(power)

#must stop pwm vibration in order to use HIGH and LOW power vibrations
def stop_pwm_vibration():
    #MUST be called before using vibrate_for_seconds
    motor_pwm.stop()

#Reads temperature sensor
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


def check_button1(): #button for timer, pressing toggles timer from off to on or vice versa
    #any return other than 0 means the button is pressed
    if not GPIO.event_detected(BUTTON1):
        return 0
    time.sleep(DOUBLE_PRESS_WINDOW)
    if GPIO.event_detected(BUTTON1):
        return 2
    return 1

def check_button2(): #button for temperature, any presses gives current temp
    #any return other than 0 means the button is pressed
    if not GPIO.event_detected(BUTTON2):
        return 0
    time.sleep(DOUBLE_PRESS_WINDOW)
    if GPIO.event_detected(BUTTON2):
        return 2
    return 1

#espeak function, subprocess means it runs that command externally basically runs the command in terminal
#stops script until the subprocess finishes
def speak(text):
    subprocess.run(["espeak", 130, text])

#Function for checking the timer using various rarity flags. 
#Basically, the timer constantly keeps increasing, when it reaches past a threshhold, we only
#want it to state the meat is that rarity once, so we only say it if the flag associated
#with that rarity is false, which we then set to true afterwards. 
#These flags must be reset if the timer is stopped
def timerCheck():
    global rare_flag, mediumrare_flag, medium_flag, mediumwell_flag, welldone_flag
    if(is_Timer_Running):
        timerTime = time.time() - start_Time
        if timerTime > 10: #3 minutes
            if rare_flag == False:
                speak("Meat is now Rare, Flip and reset timer")
                rare_flag = True
        if timerTime > 20: #4 minutes
            if mediumrare_flag == False:
                speak("Meat is now Medium Rare, Flip and reset timer")
                mediumrare_flag = True
        if timerTime > 300: #5 minutes
            if medium_flag == False:
                speak("Meat is now Medium, Flip and reset timer")
                medium_flag = True
        if timerTime > 360: #6 minutes
            if mediumwell_flag == False:
                speak("Meat is now Medium Well, Flip and reset timer")
                mediumwell_flag = True
        if timerTime > 400: #7 minutes
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
            if(temp >= 28): #43): #according to google, 43 degrees C is when something begins to be "too hot to touch"
                stop_pwm_vibration()
                seconds = 30/temp #higher the temp means more requent the buzzes
                vibrate_for_seconds(seconds)
            else: #if close but not high temperature, low humm pwm
                vibrate_at_power(30) #change once confirm this works
        else: #if the distance is greater than 20 cm, stop pwm vibration
            vibrate_at_power(0)
            stop_pwm_vibration()

        if (is_Timer_Running):
            timerCheck()

        presses1 = check_button1() #check button 1
        if presses1: #if there have been presses, if timer is not running, start timer, if it is, 
                     #stop it and reset everything timer related
            if read() != None:
                if(not is_Timer_Running):
                    start_Time = time.time()
                    is_Timer_Running = True
                    speak("Timer started")
                elif(is_Timer_Running):
                    start_Time = 0
                    is_Timer_Running = False
                    speak("Timer stopped")
                    rare_flag = False
                    mediumrare_flag = False
                    medium_flag = False
                    mediumwell_flag = False
                    welldone_flag = False

        presses2 = check_button2() #check button 2
        if presses2: #if pressed, speak current temperature
            if read() != None:
                temp = read()
                print ("Current temperature : %0.3f C" % temp)
                speak_message = f"Current Temperature is {temp:.2f} degrees Celsius."
                speak(speak_message)
        time.sleep(0.05)
        


def destroy(): #successfully shut down everything on code end
    motor_pwm.stop()
    GPIO.cleanup()

if __name__ == "__main__": #main function so code runs properly
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
