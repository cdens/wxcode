#!/usr/bin/env python3 

import time, datetime
import RPi.GPIO as GPIO

global counts

def voltageChangeCallbackCounter(pin):
    
    global counts
    if not GPIO.input(pin):
        counts = counts + 1

def countSensorTriggers(pin,duration):

    #initializing counter
    global counts
    counts = 0

    #setting switch GPIO as input, pull high voltage by default
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pin, GPIO.BOTH, callback=voltageChangeCallbackCounter, bouncetime=10)
    
    tt = 0
    dt = 0.05
    
    while tt <= duration:
        time.sleep(dt)
        tt += dt
    
    GPIO.cleanup()

    return counts


def pollanemometer():

    #get number of anemometer rotations in 30 seconds (GPIO17/pin11)
    dt = 30
    counts = countSensorTriggers(17,dt)
    
    #convert counts to wind speed (mph)
    # speed (in/sec) = 2*pi*r/t (r=10 in, t = dt -> default 30sec)
    # 1 in/sec = 0.056818 mph
    # conversion = 2*pi*10 inches * 0.056818 = 3.569887506
    wspd = counts*3.569887506/dt
    
    #calibration factor for wind energy loss
    wspd = wspd*1.2

    return wspd


if __name__ == "__main__":
    print(f"[+] Starting wind speed measurement for 30 seconds")
    wspd = pollanemometer()
    print(f"Measured wind speed: {wspd} mph")

