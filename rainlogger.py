#!/usr/bin/env python3 

import time
from datetime import datetime
import RPi.GPIO as GPIO


def voltageChangeCallbackCounter(pin):
    
    with open(".config") as c:
        logfile = c.read().split("\n")[2].split(' ')[1].strip()

    with open(logfile,"a") as f:
        f.write("switch\n")
    
    print(f"[+] Rain bucket tip detected ({datetime.strftime(datetime.utcnow(),'%Y%m%d %H:%M:%S')} UTC)")


def logBucketTips(pin):

    #setting switch GPIO as input, pull high voltage by default
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pin, GPIO.BOTH, callback=voltageChangeCallbackCounter, bouncetime=10)
    
    print("[+] Rain logger configured, waiting for bucket tips")

    while True:
        time.sleep(10)
    
    GPIO.cleanup()



def runRainLogger():

    with open(".config") as c:
        lines = c.read().split("\n")
        logfile = lines[2].split(' ')[1].strip()
        dateformat = lines[3].split(' ')[1].strip()

    with open(logfile,"w") as f:
        f.write(datetime.strftime(datetime.utcnow(), dateformat) + "\n")

    print("[+] Rain logger initialized- configuring logger")

    logBucketTips(13)

if __name__ == "__main__":
    runRainLogger()
