#!/usr/bin/env python3
#Logger to record met output and save it to necessary locations
from os import path, remove
import datetime as dt
import geopy.distance
<<<<<<< HEAD
import log_bme280, winddir, webserverinteraction
=======
import log_bme280, windspeed, winddir, GPSinteract, webserverinteraction
>>>>>>> d2dd21a258d5f6d3291aba2ccd1bb2735f01fa57
import traceback

def log():
    print("[+] Getting weather observation")

    #logger config variables
    reldatadir = "../wxdata/" #relative path (slash-terminated) to data directory
    datelog = "lastob" #where time of last observation is stored
    filedateformat = "%Y%m%d" #date format for wx observation CSV files

    #logger config variables from file
    with open(".config") as c:
        lines = c.read().split("\n")
        password = lines[0].split(' ')[1]
        lightninglogfile = lines[1].split(' ')[1]
        rainlogfile = lines[2].split(' ')[1]
        dateformat = lines[3].split(' ')[1]
        gpsfile = lines[4].split(' ')[1]
        gpsport = lines[5].split(' ')[1]

    #getting current datetime
    curdatetime = dt.datetime.utcnow()
    curdatetimestr = curdatetime.strftime(dateformat) #converting datetime to string

    #checking GPS position
    print("[+] Checking GPS position")
    lat,lon,_,flag = GPSinteract.getcurrentposition(gpsport,10)
    needsGPSupdate = False
    if flag == 0:
        if not path.exists(gpsfile): #identify + save GPS position if one isn't saved
            print(f"[+] GPS file does not exist- logging position: lat={lat}, lon={lon}")
            needsGPSupdate = True
        else: #checking for position change by 1 km or more
            isGood,lastlat,lastlon = GPSinteract.readGPSfile(gpsfile)
            if isGood and geopy.distance.distance((lat,lon),(latlat,lastlon)).km >= 1:
                print(f"[+] GPS position changed by more than 1 km, from (lat={lastlat}, lon={lastlon}) to (lat={lat}, lon={lon})), logging new position")
                needsGPSupdate = True
    elif flag == 2: #failed to open port
        print("[!] Unable to communicate with specified port for GPS fix")
    elif flag == 1: #no valid fix data (most likely receiver is connected but not getting satellite signal)
        print("[!] GPS request timed out")
  
    #uploading/storing GPS position if necessary
    if needsGPSupdate:
        print("[+] Posting updated position to webserver")
        success = webserverinteraction.postGPSpositionchange(lat,lon)
        if success:
            print("[+] Position upload successful, logging to file")
            GPSinteract.writeGPSfile(gpsfile,True,lat,lon)
        else:
            print("[-] Position upload unsuccessful, waiting until next observation to reattempt")
            
                
            


    #getting temperature/humidity/pressure
    print("[+] Getting temperature/humidity/pressure")
    try:
        T,q,P = log_bme280.get_mean_bme280_obs(20, 0.5) #mean values for 20 obs over 10 second period
    except Exception:
        print("[-] Error raised during BME280 logger call:")
        traceback.print_exc()
        T = 0
        q = 0
        P = 0
    
    #getting wind speed
    print("[+] Getting wind speed")
    try:
        wspd = windspeed.pollanemometer()
    except Exception:
        print("[-] Error raised in anemometer logger call:")
        traceback.print_exc()
        wspd = 0

    #getting wind direction 
    print("[+] Getting wind direction")
    try:
        wdir = winddir.getwinddirection()
    except Exception:
        print("[-] Error raised in wind direction logger call:")
        traceback.print_exc()
        wdir = 0

    #getting number of lightning strikes
    print("[+] Reading lightning strike data")
    strikeRate = 0
    if path.exists(lightninglogfile):
        with open(lightninglogfile) as f:
            lines = f.read().split("\n")
            lastdate = dt.datetime.strptime(lines[0].strip(),dateformat)
            dtime = (dt.datetime.utcnow() - lastdate).total_seconds() * 3600 #time in hours
            strikeRate = (len(lines) - 1)/dtime #lightning strikes per hour
        remove(lightninglogfile) #delete file
        with open(lightninglogfile,"w") as f:
            f.write(dt.datetime.strftime(curdatetime,dateformat) + "\n")
    else:
        print("[-] Lightning strike file not found!")

    #getting rainfall
    print("[+] Reading rainfall rate data")
    rainRate = 0
    if path.exists(rainlogfile):
        print("Made it here")
        with open(rainlogfile) as f:
            lines = f.read().split("\n")
            print(lines)
            lastdate = dt.datetime.strptime(lines[0].strip(),dateformat)
            print(len(lines))
            dtime = (curdatetime - lastdate).total_seconds() / 3600 #time in hours
            rainRate = (len(lines) - 1)/dtime #rainfall (mm) per hour
        remove(rainlogfile)
        with open(rainlogfile,"w") as f:
            f.write(dt.datetime.strftime(curdatetime,dateformat) + "\n")
    else:
        print("[-] Rainfall rate file not found!")

    solarVal = 0 #solar intensity (TODO)

    
    
    #line to send to file
    curline = f"{curdatetimestr}, {T:5.2f}, {q:5.2f}, {P:7.2f}, {wspd:4.1f}, {wdir:5.1f}, {strikeRate:4.2f}, {rainRate:4.2f}, {solarVal:4.1f} \n" #ob line to be transmitted
    print(f"[!] Weather Observation: {curline}")

    #POST request for website 
    url = open("serveraddress","r").read().strip()
    print("[+] Sending POST with observation to server: " + url)
    success = postregularupdate(cdtgstr,T,q,P,rainRate,wspd,wdir,strikeRate,solarVal,password,url)

    #appending data to file
    curlog = reldatadir + "WxObs" + curdatetime.strftime(filedateformat) + ".csv"
    with open(curlog,"a") as f:
        f.write(curline)

if __name__ == "__main__":
    log()
