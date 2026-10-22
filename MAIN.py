# Main program file
import RPi.GPIO as GPIO
import time
import os

TRIG = 11
ECHO = 12
VIBRATION_MOTOR = 16

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

def loop():
    #MAIN PROGRAM LOOP
    while True:
        dis = distance()
        print(f"Object detected at: {dis} cm")
        if read() != None:
            print ("Current temperature : %0.3f C" % read())

        if dis < 20: #distance less than 20 cm
            #Once temperature sensor is implemented, have an if statement first to check temperature,
            #temperature vibrations take priority to distance vibrations
            vibrate_at_power(30) #change once confirm this works
        else:
            vibrate_at_power(0)
            stop_pwm_vibration()
        


def destroy():
    motor_pwm.stop()
    GPIO.cleanup()

if __name__ == "__main__":
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        destroy()