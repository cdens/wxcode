#!/usr/bin/env python3
#Single point of control for all weather station logging functions

import subprocess, sys, time 
import rainlogger, lightninglogger, wxlogger, button_monitor


if __name__ == "__main__":
    
    print("[+] Beginning PiWxStation Logger")
    
    #Each Thread's lock system is called like
    #Thread.change_lock(True) to lock and Thread.change_lock(False) to unlock
    
    print("[+] Starting rain logging thread")
    RainThread = rainlogger.RainBucketThread()
    RainThread.start()
    print("[+] Rain logging thread initiated")
    
    print("[+] Starting lightning logging thread")
    LightningThread = lightninglogger.LightningThread()
    LightningThread.start()
    print("[+] Lightning logging thread initiated")
    
    print("[+] Starting WxStation logger loop")
    WxLogger = wxlogger.WeatherLogger()
    WxLogger.start()
    
    wxthreads = [WxLogger, LightningThread, RainThread]
    
    #listening for button inputs to start/stop weather station
    ButtonThread = button_monitor.ButtonThread()
    ButtonThread.start()
    
    while True:
        status = ButtonThread.get_status()
        
        if status:
            ButtonThread.set_status(0)
            
            #short push w/ logger inactive- start logger
            if status == 1: 
                print("Starting logging")
                for t in wxthreads:
                    t.change_lock(False)
                with open("activelogging","w") as f:
                    f.write("1")    
            
            #short push w/ logger active- log current conditions
            elif status == 2: 
                print("Collecting new weather observation")
                WxLogger.run_logger()
                
            #medium push- inactivate logger
            elif status == 3:
                print("Terminating logging") 
                for t in wxthreads:
                    t.change_lock(True)
                with open("activelogging","w") as f:
                    f.write("0")
            
            #long push- shutdown weather station  
            elif status == 4:
                print("Shutting down")
                cmd = "sudo shutdown -h now"
                subprocess.run(cmd.split())
                
        time.sleep(2) #2 second delay between input checks