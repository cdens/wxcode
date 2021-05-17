#!/usr/bin/env python3 

import time, threading, logging
from datetime import datetime
import RPi.GPIO as GPIO
from os import remove, path

Logger = logging.getLogger(__name__)

class RainBucketThread(threading.Thread):
    
    def __init__(self):
        
        super().__init__()
        
        self.pin = 13
        self._locked = bool(int(open("activelogging","r").read().strip()))
        
        with open(".config") as c:
            lines = c.read().split("\n")
            self.logfile = lines[2].split(' ')[1].strip()
            self.dateformat = lines[3].split(' ')[1].strip()
        
        if not self._locked:
            self.init_countfile()
            
        Logger.debug("[+] Rain logger initialized- configuring logger")
        
        
    def change_lock(self, status):
        self._locked = status
        if not self._locked:
            self.init_countfile()
    
    def init_countfile(self):
        if path.exists(self.logfile):
            remove(self.logfile)
        with open(self.logfile,"w") as f:
            f.write(datetime.strftime(datetime.utcnow(), self.dateformat) + "\n")
        
    def logBucketTips(self,pin):
        
        def voltageChangeCallbackCounter(pin):
            if not self._locked:
                with open(self.logfile,"a") as f:
                    f.write("switch\n")
    
        Logger.debug(f"[+] Rain bucket tip detected ({datetime.strftime(datetime.utcnow(),'%Y%m%d %H:%M:%S')} UTC)")
    
        #setting switch GPIO as input, pull high voltage by default
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=voltageChangeCallbackCounter, bouncetime=10)
        
        Logger.debug("[+] Rain logger configured, waiting for bucket tips")
    
        while True:
            time.sleep(10)
        
        
    def run(self):
        try:
            self.logBucketTips(self.pin)
        except KeyboardInterrupt:
            GPIO.cleanup()
        except Exception as e:
            Logger.exception(e)
    
    
    
if __name__ == "__main__":
    runRainLogger()
