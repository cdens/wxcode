#!/usr/bin/env python3

#Single point of control for all weather station logging functions

import threading, sys, time 
from datetime import datetime
import numpy as np
import rainlogger, lightninglogger, wxlogger

if __name__ == "__main__":
    
    print("[+] Beginning PiWxStation Logger")
    
    #starting separate threads for lightning and rain logging since those sensors must be monitored constantly
    print("[+] Starting rain logging thread")
    rainThread = threading.Thread(target=rainlogger.runRainLogger)
    rainThread.start()
    print("[+] Rain logging thread initiated")
    
    print("[+] Starting lightning logging thread")
    LightningThread = lightninglogger.LightningThread()
    LightningThread.start()
    print("[+] Lightning logging thread initiated")
        
    #specify interval (minutes) for observations
    intervalmin = 15 #minutes
    intervalsec = intervalmin*60 #to seconds
    
    try:
        
        lastob = datetime.utcnow()
        lastob = lastob.replace(year=1, second=0)
        
        #infinitely looping, getting observation every 15 minutes
        while True:
            
            if int(open("activelogging","r").read().strip()):
                cdt = datetime.utcnow()
                if (cdt - lastob).total_seconds() >= intervalsec:
                    print(f"[+] Starting wxlogger for observation time {datetime.strftime(cdt,'%Y%m%d %H:%M')} UTC")
                    wxlogger.log(LightningThread)
                    print(f"[+] Finished wxlogger for observation time {datetime.strftime(cdt,'%Y%m%d %H:%M')} UTC")
                    lastob = cdt
            
            time.sleep(10) #10 second sleep between time checks
                    
        
    except KeyboardInterrupt:
        print("[!] Keyboard interrupt detected- cleaning up and exiting")
        sys.exit()
