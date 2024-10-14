#!/usr/bin/env python3
#Single point of control for all weather station logging functions

import subprocess, sys, time, logging
import logging.config
import rainlogger, lightninglogger, wxlogger, button_monitor, configupdate
from datetime import datetime


def main(url, needsGPSupdate):
    
    Logger.info(f"[+] Beginning PiWxStation Logger")
    #Each Thread's lock system is called following:
    #Thread.change_lock(True) to lock and Thread.change_lock(False) to unlock
    
    wxthreads = []
    
    #no point in encasing this in a try statement as the program can't run without it
    Logger.info("[+] Starting configuration thread")
    ConfigThread = configupdate.ConfigThread(".config")
    ConfigThread.run()
    config = ConfigThread.config
    
    Logger.info("[+] Starting rain logging thread")
    try:
        RainThread = rainlogger.RainBucketThread(config)
        Logger.debug("[+] Rain logging thread initiated")
        wxthreads.append(RainThread)
    except Exception as e:
        Logger.error("[!] Rain logger failed to initiate")
        Logger.exception(e)
    
    Logger.debug("[+] Starting lightning logging thread")
    try:
        LightningThread = lightninglogger.LightningThread(config)
        Logger.info("[+] Lightning logging thread initiated")
        wxthreads.append(LightningThread)
    except Exception as e:
        Logger.error("[!] Lightning logger failed to initiate")
        Logger.exception(e)
    
    Logger.debug("[+] Starting WxStation logger loop")
    try:
        WxLogger = wxlogger.WeatherLogger(config)
        wxthreads.append(WxLogger)
    except Exception as e:
        Logger.error("[!] WxStation logger failed to initiate")
        Logger.exception(e)
    
    try:
        for thread in wxthreads:
            thread.start()
    except Exception as e:
        Logger.error("[!] Failed to start running a thread")
        Logger.exception(e)
        
    #listening for button inputs to start/stop weather station
    try:
        ButtonThread = button_monitor.ButtonThread()
        ButtonThread.start()
    except Exception as e:
        Logger.error("[!] Error initiating button monitoring thread!")
        Logger.exception(e)
    
        
    #button monitoring loop waiting to adjust WxStation behavior based on user input
    while True:
        status = ButtonThread.get_status()
        
        if status:
            ButtonThread.change_status(0)
            
            #short push w/ logger inactive- start logger
            if status == 1: 
                Logger.debug("Button press- starting logging")
                for t in wxthreads:
                    t.change_lock(False)
                with open("activelogging","w") as f:
                    f.write("1")    
            
            #short push w/ logger active- log current conditions
            elif status == 2: 
                Logger.debug("Button press- collecting new weather observation")
                WxLogger.run_logger() 
                
            #medium push- inactivate logger
            elif status == 3:
                Logger.debug("Button press- terminating logging") 
                for t in wxthreads:
                    t.change_lock(True)
                with open("activelogging","w") as f:
                    f.write("0")
            
            #long push- shutdown weather station  
            elif status == 4:
                Logger.debug("Button press- shutting down")
                cmd = "sudo shutdown -h now"
                subprocess.run(cmd.split())
                
        
        #if configuration file has been updated- push updates to individual threads
        if ConfigThread.get_status():
            config = ConfigThread.config
            ConfigThread.set_status(False)
            for t in wxthreads:
                t.change_config(config)
                
        time.sleep(2) #2 second delay between input checks


    
if __name__ == "__main__":
    
    debugging = True
    
    #first GPS cycle will automatically be pushed to webserver
    url = open("serveraddress","r").read().strip()
    needsGPSupdate = True
    
    currentLevel = logging.INFO #DEBUG, INFO, WARNING, ERROR
    dtgstr = datetime.strftime(datetime.utcnow(),"%Y%m%d%H%M")
    logfile = f"wxinfo_{dtgstr}.log"
    
    print(f"Starting PiWxStation- appending log information to {logfile}")
    
    #creating logger
    Logger = logging.getLogger(__name__)
    if debugging:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename=logfile)
    else:
        logging.basicConfig(level=currentLevel, format='%(asctime)s - %(levelname)s - %(message)s', filename=logfile)
    
    main(url, needsGPSupdate)
    
    
    
    
    