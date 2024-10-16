#!/usr/bin/env python3
#Logger to record met output and save it to necessary locations
from os import path, remove
import datetime as dt
import threading, logging, traceback
import geopy.distance
import log_bme280, windspeed, winddir, GPSinteract
import webserverinteraction as web
from time import sleep
import numpy as np

Logger = logging.getLogger(__name__)


class WeatherLogger(threading.Thread):
    
    def __init__(self, config):
        super().__init__()
        
        self.change_config(config)
        
        #specify interval (minutes) for observations
        self.isLogging = False
        self.intervalmin = 15 #minutes
        self.intervalsec = self.intervalmin*60 #to seconds
        self.locked = False
        
        #wind speed logger
        self.wspdintervalmin = 1
        self.wspdintervalsec = self.wspdintervalmin * 60
        self.lastwspdlog = dt.datetime(1,1,1)
        self.wspdlist = []
        
        self.needsGPSupdate = False #doesn't need to update GPS as long as within previous fix's margin of error
        
        cdtgstr = dt.datetime.utcnow().strftime(config["dateformat"])
        web.send_email("Logger Initialized", "WxStation Logger Initialized, DTG " + cdtgstr, config["emailaccount"], [config["emailaccount"]], config["emailpassword"])
        
    def change_lock(self,status):
        self.locked = bool(int(open("activelogging","r").read().strip()))
    
    def change_config(self, config):
        self.config = config
        
    def get_logging_status(self):
        return self.isLogging
        
    def set_logging_status(self,status):
        self.isLogging = status
        
    def run_logger(self):
        if not self.isLogging:
            self.isLogging = True
            self.needsGPSupdate = log(self.config, self.needsGPSupdate, self.wspdlist)
            self.isLogging = False
            
        
    def run(self):
        try:
            #infinitely looping, getting observation every 15 minutes
            while True:
                if int(open("activelogging","r").read().strip()) and not self.locked:
            
                    #getting last observation time, default to something more than logging interval period
                    try:
                        lastob = dt.datetime.strptime(open("lastob","r").read().strip(), '%Y%m%d %H:%M')
                    except FileNotFoundError:
                        lastob = dt.datetime(1,1,1) #definitely more than 15 minutes ago
                        
                    cdt = dt.datetime.utcnow()
                    
                    #getting new wind speed observation
                    if (cdt - self.lastwspdlog).total_seconds() >= self.wspdintervalsec:
                        #getting wind speed
                        logging.debug("[+] Getting wind speed")
                        try:
                            self.wspdlist.append(windspeed.pollanemometer(dt=5))
                            self.lastwspdlog = cdt
                        except Exception as e:
                            Logger.exception(e)
                    
                    if (cdt - lastob).total_seconds() >= self.intervalsec:
                        
                        Logger.info(f"[+] Starting wxlogger for observation time {dt.datetime.strftime(cdt,'%Y%m%d %H:%M')} UTC")
                        self.run_logger()
                        Logger.debug(f"[+] Finished wxlogger for observation time {dt.datetime.strftime(cdt,'%Y%m%d %H:%M')} UTC")
                        
                        #resetting wind speed logging
                        self.wspdlist = []                        
                        with open("lastob","w") as f:
                            f.write(dt.datetime.strftime(cdt,'%Y%m%d %H:%M'))
                            
                    sleep(30) #30 second sleep between time checks
                        
        except KeyboardInterrupt:
            Logger.error("[!] Keyboard interrupt detected- cleaning up and exiting")
            sys.exit()
        except Exception as e:
            Logger.exception(e)
            



def log(config, needsGPSupdate, wspdlist):
    
    Logger.debug("[+] Getting weather observation")

    #logger config variables
    reldatadir = "../wxdata/" #relative path (slash-terminated) to data directory
    datelog = "lastob" #where time of last observation is stored
    filedateformat = "%Y%m%d" #date format for wx observation CSV files

    #getting current datetime
    curdatetime = dt.datetime.utcnow()
    curdatetimestr = curdatetime.strftime(config["dateformat"]) #converting datetime to string

    #checking GPS position
    Logger.debug("[+] Checking GPS position")
    lat,lon,_,flag = GPSinteract.getcurrentposition(config["gpsport"],config["gpsbaud"],10)
    if flag == 0:
        if not path.exists(config["gps"]): #identify + save GPS position if one isn't saved
            Logger.warning(f"[+] GPS file does not exist- logging position: lat={lat}, lon={lon}")
            GPSinteract.writeGPSfile(config["gps"],1,lat,lon)
            needsGPSupdate = True
        else: #checking for position change by 1 km or more
            isGood,lastlat,lastlon = GPSinteract.readGPSfile(config["gps"])
            if isGood and geopy.distance.distance((lat,lon),(lastlat,lastlon)).km >= 1:
                Logger.info(f"[+] GPS position changed by more than 1 km, from (lat={lastlat}, lon={lastlon}) to (lat={lat}, lon={lon})), logging new position")
                GPSinteract.writeGPSfile(config["gps"],1,lat,lon)
                needsGPSupdate = True
    elif flag == 2: #failed to open port
        Logger.error("[!] Unable to communicate with specified port for GPS fix")
        needsGPSupdate = False
    elif flag == 1: #no valid fix data (most likely receiver is connected but not getting satellite signal)
        Logger.error("[!] GPS request timed out")
        needsGPSupdate = False
  
    #uploading/storing GPS position if necessary
    if needsGPSupdate:
        Logger.debug("[+] Posting updated position to webserver")
        success = web.postGPSpositionchange(lat,lon,config["password"],config["url"])
        if success:
            Logger.debug("[+] Position upload successful, logging to file")
            needsGPSupdate = False #update complete
        else:
            Logger.warning("[-] Position upload unsuccessful, waiting until next observation to reattempt")


    #getting temperature/humidity/pressure
    Logger.debug("[+] Getting temperature/humidity/pressure")
    try:
        T,q,P = log_bme280.get_mean_bme280_obs(20, 0.5) #mean values for 20 obs over 10 second period
    except Exception as e:
        Logger.exception(e)
        T = 0
        q = 0
        P = 0
    
    #getting wind speed
    logging.debug("[+] Calculating mean and max wind speed for current interval")
    try:
        if len(wspdlist) > 0:
            logging.warning("[!] No wind speed measurements for the current observation period ")
            wspdarray = np.asarray(wspdlist)
            wspd = np.nanmean(wspdarray)
            wgust = np.nanmax(wspdarray)
        else:
            wspd = 0
            wgust = 0
    except Exception as e:
        Logger.exception(e)
        wspd = 0
        wgust = 0

    #getting wind direction 
    Logger.debug("[+] Getting wind direction")
    try:
        wdir = winddir.getwinddirection()
    except Exception as e:
        Logger.exception(e)
        wdir = 0

    #getting number of lightning strikes
    Logger.debug("[+] Reading lightning strike data")
    strikeRate = 0
    if path.exists(config["lightning"]):
        with open(config["lightning"]) as f:
            lines = f.read().split("\n")
            lastdate = dt.datetime.strptime(lines[0].strip(),config["dateformat"])
            dtime = (dt.datetime.utcnow() - lastdate).total_seconds() * 3600 #time in hours
            strikeRate = (len(lines) - 2)/dtime #lightning strikes per hour
        remove(config["lightning"]) #delete file
        with open(config["lightning"],"w") as f:
            f.write(dt.datetime.strftime(curdatetime,config["dateformat"]) + "\n")
    else:
        Logger.error("[-] Lightning strike file not found!")

    #getting rainfall
    Logger.debug("[+] Reading rainfall rate data")
    rainRate = 0
    if path.exists(config["rain"]):
        with open(config["rain"]) as f:
            lines = f.read().split("\n")
            Logger.debug("File " + config["rain"] + ': ' + ', '.join(lines))
            lastdate = dt.datetime.strptime(lines[0].strip(),config["dateformat"])
            dtime = (curdatetime - lastdate).total_seconds() / 3600 #time in hours
            rainRate = (len(lines) - 2)/dtime #rainfall (mm) per hour
        remove(config["rain"])
        with open(config["rain"],"w") as f:
            f.write(dt.datetime.strftime(curdatetime,config["dateformat"]) + "\n")
    else:
        Logger.error("[-] Rainfall rate file not found!")

        
    solarVal = 0 #solar intensity (TODO)

    
    #line to send to file
    curline = f"{curdatetimestr}, {T:5.1f}, {q:5.1f}, {P:7.1f}, {wspd:4.1f}, {wgust:4.1f}, {wdir:03.0f}, {strikeRate:4.1f}, {rainRate:4.1f}, {solarVal:4.1f}" #ob line to be transmitted
    Logger.info(f"[!] Weather Observation: {curline}")

    #POST request for website 
    Logger.debug("[+] Sending POST with observation to server: " + config["url"])
    success = web.postregularupdate(curdatetimestr, T,q,P, rainRate, wspd, wgust, wdir, strikeRate, solarVal, config["password"], config["url"], config["emailaccount"], config["emailpassword"])

    #appending data to file
    curlog = reldatadir + "WxObs" + curdatetime.strftime(filedateformat) + ".csv"
    with open(curlog,"a") as f:
        f.write(curline + "\n")
        
    return needsGPSupdate
    
    
    
