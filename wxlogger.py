#!/usr/bin/env python3
#Logger to record met output and save it to necessary locations
from os import path, remove
import datetime as dt
import log_bme280


#logger config variables
reldatadir = "../wxdata/" #relative path (slash-terminated) to data directory
datelog = "lastob" #where time of last observation is stored
dateformat = "%Y%m%d %H:%M" #universal system date format
filedateformat = "%Y%m%d" #date format for wx observation CSV files
#recentlog = "recent_data.csv" #high res obs csv
#recentrange = 4 #how many hours back do high res obs go


#getting current datetime, wx observations
cdt = dt.datetime.utcnow()
cdtstr = cdt.strftime(dateformat) #converting datetime to string
T,q,P = log_bme280.retrieve_bme280_ob()
curline = f"{cdtstr}, {T:5.2f}, {q:5.2f}, {P:7.2f} \n" #ob line to be transmitted

#appending data to file
curlog = reldatadir + "WxObs" + cdt.strftime(filedateformat) + ".csv"

with open(curlog,"a") as f:
    f.write(curline)

