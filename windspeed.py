#!/usr/bin/env python3 

import time, datetime, logging
import RPi.GPIO as GPIO

Logger = logging.getLogger(__name__)

class WindSpeedLogger:

    def __init__(self):
        self.counts = 0

    def countSensorTriggers(self,pin,duration):

        #initializing counter
        self.counts = 0
        
        #creating callback function (creating inside of function so callback has access to self):
        def voltageChangeCallbackCounter(pin):
            if not GPIO.input(pin):
                self.counts += 1


        #setting switch GPIO as input, pull high voltage by default
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.BOTH, callback=voltageChangeCallbackCounter, bouncetime=10)
        
        tt = 0
        dt = 0.05
        
        while tt <= duration:
            time.sleep(dt)
            tt += dt
        
        GPIO.remove_event_detect(pin)

        return self.counts


    def pollanemometer(self):

        #get number of anemometer rotations in 30 seconds (GPIO17/pin11)
        dt = 10 
        counts = self.countSensorTriggers(17,dt) #divide by 2 since polls twice per rotation
        rotations = counts/2
        
        #convert counts to wind speed (mph)
        # speed (in/sec) = 2*pi*r/t (r=10 in, t = dt -> default 30sec)
        # 1 in/sec = 0.056818 mph
        # conversion = 2*pi* 2.5 inches * 0.056818 = 0.8925
        wspd = rotations*0.8925/dt
        
        
        Logger.debug(f"Measured wind speed: {counts} counts, {rotations} rotations, {wspd} mph uncalibrated")
        
        #calibration factor for wind energy loss
        #wspd = wspd*1.2

        return wspd

def pollanemometer():
    spdcheck = WindSpeedLogger()
    return spdcheck.pollanemometer() #returns wind speed

if  __name__ == "__main__":
    Logger.debug(f"[+] Starting wind speed measurement for 10 seconds")
    wspd = pollanemometer()

