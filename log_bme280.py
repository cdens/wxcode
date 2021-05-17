#!/usr/bin/env python3

import bme280, smbus2, time, logging

Logger = logging.getLogger(__name__)

#retrieve and return single observation from BME280 (function called by WxStation Logger)
def retrieve_bme280_ob():
    bus, address = set_bme280_i2c()

    port = 1 
    address = 0x77
    with smbus2.SMBus(port) as bus:
        bme280.load_calibration_params(bus,address)
        
        obs = bme280.sample(bus,address)
        q = obs.humidity
        P = obs.pressure
        T = obs.temperature
    
    return T,q,P 


#log BME280 T/q/P output to command line (1 second sampling frequency)
def log_bme280_to_cmd():
    port = 1 
    address = 0x77
    with smbus2.SMBus(port) as bus:
        bme280.load_calibration_params(bus,address)
        
        while True:
            obs = bme280.sample(bus,address)
            q = obs.humidity
            P = obs.pressure
            T = obs.temperature
            
            Logger.debug(f"\r [+] Temperature: {T:5.2f} degC, Humidity: {q:5.2f} %, Pressure: {P:6.1f} mb", end=" ")
            time.sleep(1)
 

#retrieve mean value from # of obs over interval
def get_mean_bme280_obs(num,dt):
    
    if num < 1:
        num = 1
    if dt <= 0.1:
        dt = 0.1
    
    no = 0
    temp = 0.
    rh = 0.
    pres = 0.

    Logger.debug("[+] Starting BME280 obs")

    port = 1 
    address = 0x77
    with smbus2.SMBus(port) as bus:
        bme280.load_calibration_params(bus,address)
       
        while no < num:
            obs = bme280.sample(bus,address)
            q = obs.humidity
            P = obs.pressure
            T = obs.temperature
        
            no += 1
            temp += T
            rh += q
            pres += P

            Logger.debug(f"[+] Got observation {no} of {num}")
            
            time.sleep(dt)
        
    temp = temp/no
    rh = rh/no
    pres = pres/no
    
    Logger.debug("[+] Finished BME280 observation cycle")

    return temp, rh, pres
    

#if function is called, run log to command line
if __name__ == "__main__":
    log_bme280_to_cmd()
