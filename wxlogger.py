#!/usr/bin/env python3
#Logger to record met output and save it to necessary locations
from os import path, remove
import datetime as dt
import log_bme280, winddir
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

    #getting current datetime
    cdt = dt.datetime.utcnow()
    cdtstr = cdt.strftime(dateformat) #converting datetime to string

    #trying for GPS position, checking against known position (TODO)


    #getting temperature/humidity/pressure
    print("[+] Getting temperature/humidity/pressure")
    try:
        T,q,P = log_bme280.get_mean_bme280_obs(20, 0.5) #mean values for 20 obs over 10 second period
    except Exception:
        print("[-] Error raised during BME280 logger call:")
        traceback.print_exc()
    
    #getting wind speed
    print("[+] Getting wind speed")
    try:
        wspd = pollanemometer()
    except Exception:
        print("[-] Error raised in anemometer logger call:")
        traceback.print_exc()

    #getting wind direction 
    print("[+] Getting wind direction")
    try:
        wdir = winddir.getwinddirection()
    except Exception:
        print("[-] Error raised in wind direction logger call:")
        traceback.print_exc()

    #getting number of lightning strikes
    print("[+] Reading lightning strike data")
    strikeRate = 0
    if path.exists(lightninglogfile):
        with open(lightninglogfile) as f:
            lines = f.read().split("\n")
            lastdate = dt.datetime.strptime(lines[1].strip(),dateformat)
            dtime = (dt.datetime.utcnow() - lastdate).total_seconds() * 3600 #time in hours
            strikeRate = (len(lines) - 1)/dtime #lightning strikes per hour
        remove(lightninglogfile) #delete file
        with open(lightninglogfile) as f:
            f.write(dt.datetime.strftime(curtime,dateformat) + "\n")

    #getting rainfall
    print("[+] Reading rainfall rate data")
    rainRate = 0
    if path.exists(rainlogfile):
        with open(rainlogfile) as f:
            lines = f.read().split("\n")
            lastdate = dt.datetime.strptime(lines[1].strip(),dateformat)
            dtime = (curtime - lastdate).total_seconds() * 3600 #time in hours
            strikeRate = (len(lines) - 1)/dtime #rainfall (mm) per hour
        remove(rainlogfile)
        with open(rainlogfile) as f:
            f.write(dt.datetime.strftime(curtime,dateformat) + "\n")

    #line to send to file (TODO)
    curline = f"{cdtstr}, {T:5.2f}, {q:5.2f}, {P:7.2f}, {wspd:4.1f}, {wdir:5.1f}, {strikeRate:4.1f}, {rainRate:4.1f} \n" #ob line to be transmitted
    print(f"[!] Weather Observation: {curline}")

    #POST request for website (TODO)
    print("[+] Sending POST with observation to web server")

    #appending data to file
    curlog = reldatadir + "WxObs" + cdt.strftime(filedateformat) + ".csv"
    with open(curlog,"a") as f:
        f.write(curline)

