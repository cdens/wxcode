#!/usr/bin/env python3
# WxStation web server interaction (data upload)
import requests, datetime



def postlightningstrike(dist,energy):
    test = 1
    return


def postregularupdate(cdtgstr,T,q,P,rainRate,wspd,wdir,numStrikes,solarVal,password,url):
    success = False 
    
    myobj = {'credential': password,
                'date':cdtgstr,
                'ta':str(round(T,1)), #temperature (C)
                'rh':str(round(q,1)), #relative humidity (%)
                'pres':str(round(P,1)), #pressure (mbar or hPa)
                'wspd':str(round(wspd,1)), #wind speed (m/s)
                'wdir':str(wspd), #wind direction (rel to N)
                'precip':str(round(rainRate,1)), #precipitation since last ob (cm)
                'solar':str(solarVal), #downwelling shortwave radiation at surface (J/m^2)
                'strikes':str(numStrikes)} #number lightning strikes in period

    req = requests.post(url, data = myobj, timeout = 10)
    
    if x.text == "SUCCESS":
        success = True
    else:
        success = False
        print(f"[!] Server update error for ob {cdtgstr}: {x.text}")

    return success


def postGPSpositionchange(lat,lon):
    success = False
    return success
