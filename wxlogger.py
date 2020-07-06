#!/usr/bin/env python3
#Logger to record met output and save it to necessary locations
from os import path, remove
import datetime as dt
import log_bme280, winddir


#logger config variables
reldatadir = "../wxdata/" #relative path (slash-terminated) to data directory
datelog = "lastob" #where time of last observation is stored
dateformat = "%Y%m%d %H:%M" #universal system date format
filedateformat = "%Y%m%d" #date format for wx observation CSV files

#getting current datetime
cdt = dt.datetime.utcnow()
cdtstr = cdt.strftime(dateformat) #converting datetime to string

#getting temperature/humidity/pressure
T,q,P = log_bme280.get_mean_bme280_obs(20, 0.5) #mean values for 20 obs over 10 second period

#getting wind speed
wspd = pollanemometer()

#trying for GPS position, checking against known position (TODO)


#getting number of lightning strikes (TODO)


#getting rainfall (TODO)


#getting wind direction 
wdir = winddir.getwinddirection()

#line to send to file (TODO)
curline = f"{cdtstr}, {T:5.2f}, {q:5.2f}, {P:7.2f} \n" #ob line to be transmitted

#POST request for website (TODO)


#appending data to file
curlog = reldatadir + "WxObs" + cdt.strftime(filedateformat) + ".csv"

with open(curlog,"a") as f:
    f.write(curline)

