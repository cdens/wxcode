#!/usr/bin/env python3
#Single point of control for all weather station logging functions

import subprocess, sys, time, logging
import logging.config
import rainlogger, lightninglogger, wxlogger, button_monitor
from datetime import datetime


def main(url, needsGPSupdate):
    
    Logger.info(f"[+] Beginning PiWxStation Logger")
    #Each Thread's lock system is called following:
    #Thread.change_lock(True) to lock and Thread.change_lock(False) to unlock
    
    Logger.debug("[+] Starting rain logging thread")
    try:
        RainThread = rainlogger.RainBucketThread()
        RainThread.start()
        Logger.debug("[+] Rain logging thread initiated")
    except Exception as e:
        Logger.error("[!] Rain logger failed to initiate")
        Logger.exception(e)
    
    Logger.debug("[+] Starting lightning logging thread")
    try:
        LightningThread = lightninglogger.LightningThread(url=url)
        LightningThread.start()
        Logger.debug("[+] Lightning logging thread initiated")
    except Exception as e:
        Logger.error("[!] Lightning logger failed to initiate")
        Logger.exception(e)
    
    Logger.debug("[+] Starting WxStation logger loop")
    WxLogger = wxlogger.WeatherLogger(url=url, needsGPSupdate=needsGPSupdate)
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
                Logger.debug("Button press- starting logging")
                for t in wxthreads:
                    t.change_lock(False)
                with open("activelogging","w") as f:
                    f.write("1")    
            
            #short push w/ logger active- log current conditions
            elif status == 2: 
                Logger.debug("Button press- collecting new weather observation")
                WxLogger.run_logger(url, True) #pushing button will autoupdate GPS position for webserver
                
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
                
        time.sleep(2) #2 second delay between input checks


    
if __name__ == "__main__":
    
    debugging = True
    
    #first GPS cycle will automatically be pushed to webserver
    url = open("serveraddress","r").read().strip()
    needsGPSupdate = True
    
    currentLevel = logging.DEBUG #DEBUG, INFO, WARNING, ERROR
    dtgstr = datetime.strftime(datetime.utcnow(),"%Y%m%d%H%M")
    logfile = f"wxinfo_{dtgstr}.log"
    
    print(f"Starting PiWxStation- appending log information to {logfile}")
    
    #creating logger
    Logger = logging.getLogger(__name__)
    if debugging:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=currentLevel, format='%(asctime)s - %(levelname)s - %(message)s', filename=logfile)
    
    main(url, needsGPSupdate)
    
    
    
    
    