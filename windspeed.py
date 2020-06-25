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

    #get number of anemometer rotations in 10 seconds (GPIO17/pin11)
    counts = countSensorTriggers(17,10) 

    #TODO:convert counts to wind speed (mph)
    wspd = counts*1.5 #example (incorrect)

    return wspd


if __name__ == "__main__":
    wspd = pollanemometer()

