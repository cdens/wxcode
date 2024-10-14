#!/usr/bin/env python3
# WxStation web server interaction (data upload)
import requests, datetime, logging


import smtplib
from email.mime.text import MIMEText

Logger = logging.getLogger(__name__)


def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    Logger.debug("Message sent!")


    
def postlightningstrike(dist,dtg,password,url): #TODO: send lightning updates to server
    myobj = {'credential': password,
            'date':dtg,
            'distance':str(round(dist,0))} #number lightning strikes in period
    ext = "/strikereport"
    
    try:
        req = requests.post(url + ext, data = myobj, timeout = 10)
        
        if req.text == "SUCCESS":
            return True
        else:
            Logger.error(f"[!] Lightning POST returned non success code: {req.text}")
            
    except Exception as e:
        Logger.warning(f"[!] Unable to connect to {url+ext}")       
        
    return False





def postGPSpositionchange(lat,lon,password,url): #TODO: send GPS position updates to server
    myobj = {'credential': password,
            'latitude':str(round(lat,2)),
            'longitude':str(round(lon,2))} #number lightning strikes in period
    ext = "/updateGPS"
    
    try:
        req = requests.post(url + ext, data = myobj, timeout = 10)
        
        if req.text == "SUCCESS":
            return True
        else:
            Logger.error(f"[!] GPS POST returned non success code: {req.text}")
            
    except Exception as e:
        Logger.warning(f"[!] Unable to connect to {url+ext}")       
        
    return False
    
    
    
    
    
def postregularupdate(cdtgstr, T, q, P, rainRate, wspd, wdir, numStrikes, solarVal, password, url, emailaccount, emailpassword, curline):
    
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
    ext = "/addnewob"
    
    try:
        
        send_email(f"WxUpdate {cdtgstr}", curline, emailaccount, [emailaccount], emailpassword)
        
        req = requests.post(url + ext, data = myobj, timeout = 10)
        
        if req.text == "SUCCESS":
            return True
        else:
            Logger.error(f"[!] WxObs POST returned non success code: {req.text}")
            
    except Exception as e:
        Logger.warning(f"[!] Unable to connect to {url+ext}")       
        
            
    return False
    
    
    