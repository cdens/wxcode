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
    return True
    # try:
    #     req = requests.post(url + ext, data = myobj, timeout = 10)
        
    #     if req.text == "SUCCESS":
    #         return True
    #     else:
    #         Logger.error(f"[!] Lightning POST returned non success code: {req.text}")
            
    # except Exception as e:
    #     Logger.warning(f"[!] Unable to connect to {url+ext}")
    #     Logger.debug("Traceback: " + repr(e))   
        
    # return False





def postGPSpositionchange(lat,lon,password,url): #TODO: send GPS position updates to server
    myobj = {'credential': password,
            'latitude':str(round(lat,2)),
            'longitude':str(round(lon,2))} #number lightning strikes in period
    ext = "/updateGPS"
    return True
    # try:
    #     req = requests.post(url + ext, data = myobj, timeout = 10)
        
    #     if req.text == "SUCCESS":
    #         return True
    #     else:
    #         Logger.error(f"[!] GPS POST returned non success code: {req.text}")
            
    # except Exception as e:
    #     Logger.warning(f"[!] Unable to connect to {url+ext}")
    #     Logger.debug("Traceback: " + repr(e))      
        
    # return False
    
    
    
    
    
def postregularupdate(cdtgstr, T, q, P, rainRate, wspd, wdir, numStrikes, solarVal, password, url, emailaccount, emailpassword):
    
    myobj = {'credential': password,
                'date':cdtgstr,
                'ta':str(round(T,1)), #temperature (C)
                'rh':str(round(q,1)), #relative humidity (%)
                'pres':str(round(P,1)), #pressure (mbar or hPa)
                'wspd':str(round(wspd,1)), #wind speed (m/s)
                'wdir':str(wspd), #wind direction (rel to N)
                'precip':str(round(rainRate,1)), #precipitation rate (mm/hr)
                'solar':str(solarVal), #downwelling shortwave radiation at surface (J/m^2)
                'strikes':str(numStrikes)} #number lightning strikes per hour
    ext = "/addnewob"
    
    try:
        Tf = 9*T/5 + 32
        emailbody = f"{cdtgstr} Observation:\nTemperature- {Tf:5.1f} degF\nHumidity- {q:5.1f}%\nPressure- {P:7.1f} mb\nWind- {wspd:4.1f} mph brg {wdir:03.0f}T\nLightning- {numStrikes:4.1f} strikes/hr\nRainfall- {rainRate:4.1f} mm/hr" 
        logging.debug(f"Sending email to account {emailaccount}, password {emailpassword}, text:\n{emailbody}")
        send_email(f"WxUpdate {cdtgstr}", emailbody, emailaccount, [emailaccount], emailpassword)
        return True
        # req = requests.post(url + ext, data = myobj, timeout = 10)
        
        # if req.text == "SUCCESS":
        #     return True
        # else:
        #     Logger.error(f"[!] WxObs POST returned non success code: {req.text}")
            
    except Exception as e:
        Logger.warning(f"[!] Unable to transmit data to URL {url+ext} or email {emailaccount}")       
        Logger.debug("Traceback: " + repr(e))  
            
    return False
    
    
    