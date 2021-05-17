#!/usr/bin/env python3
# WxStation web server interaction (data upload)
import requests, datetime, logging

Logger = logging.getLogger(__name__)



def postlightningstrike(dist,energy,dtg,strikeurl): #TODO: send lightning updates to server
    test = 1
    return





def postGPSpositionchange(lat,lon,gpsurl): #TODO: send GPS position updates to server
    success = False
    return success
    
    
    
    
    
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
    
    try:
        req = requests.post(url, data = myobj, timeout = 10)
        if x.text == "SUCCESS":
            return True
        else:
            Logger.error(f"[!] Server returned non success code: {x.text}")
    
    except ConnectionError, ConnectionRefusedError:
        Logger.error(f"[!] Unable to connect to {url}")       
            
    except Exception as e:
        Logger.error(f"[!] Server update error for ob {cdtgstr}")
        Logger.exception(e)
        
    return False
    
    
    