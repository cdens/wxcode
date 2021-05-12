#!/usr/bin/env python3 

import time, threading
from datetime import datetime
import RPi.GPIO as GPIO
from os import remove,path



class RainBucketThread(threading.thread):
    
    def __init__(self):
        
        super().__init__()
        
        self.pin = 13
        self.locked = bool(int(open("activelogging","r").read().strip()))
        
        with open(".config") as c:
            lines = c.read().split("\n")
            self.logfile = lines[2].split(' ')[1].strip()
            self.dateformat = lines[3].split(' ')[1].strip()
        
        if not self.locked:
            self.init_countfile()
            
        print("[+] Rain logger initialized- configuring logger")
        
        
    def change_lock(self, status):
        self.locked = status
        if not self.locked:
            self.init_countfile()
    
    def init_countfile(self):
        if path.exists(self.logfile)
            remove(self.logfile)
        with open(self.logfile,"w") as f:
            f.write(datetime.strftime(datetime.utcnow(), self.dateformat) + "\n")
        
    def logBucketTips(self,pin):
        
        def voltageChangeCallbackCounter(pin):
            if not self.locked:
                with open(self.logfile,"a") as f:
                    f.write("switch\n")
    
        print(f"[+] Rain bucket tip detected ({datetime.strftime(datetime.utcnow(),'%Y%m%d %H:%M:%S')} UTC)")
    
        #setting switch GPIO as input, pull high voltage by default
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=voltageChangeCallbackCounter, bouncetime=10)
        
        print("[+] Rain logger configured, waiting for bucket tips")
    
        while True:
            time.sleep(10)
        
        
    def run(self):
        try:
            self.logBucketTips(self.pin)
        except KeyboardInterrupt:
            GPIO.cleanup()
    
    
    
if __name__ == "__main__":
    runRainLogger()
