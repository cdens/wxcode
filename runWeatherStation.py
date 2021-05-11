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
    
    
    time.sleep(2)
    print("[+] Starting WxStation logger loop")
    
    try:
        
        #infinitely looping, getting observation every 15 minutes
        while True:
            
            if int(open("activelogging","r").read().strip()):
                
                try:
                    lastob = datetime.strptime(open("lastob","r").read().strip())
                except FileNotFoundError:
                    lastob = datetime(1,1,1) #definitely more than 15 minutes ago
                    
                cdt = datetime.utcnow()
                if (cdt - lastob).total_seconds() >= intervalsec:
                    print(f"[+] Starting wxlogger for observation time {datetime.strftime(cdt,'%Y%m%d %H:%M')} UTC")
                    wxlogger.log(LightningThread)
                    print(f"[+] Finished wxlogger for observation time {datetime.strftime(cdt,'%Y%m%d %H:%M')} UTC")
                    
                    with open("lastob","w") as f:
                        f.write(datetime.strftime(lastob,'%Y%m%d %H:%M'))
            
            time.sleep(30) #30 second sleep between time checks
                    
        
    except KeyboardInterrupt:
        print("[!] Keyboard interrupt detected- cleaning up and exiting")
        sys.exit()
