#!/usr/bin/env python3

import bme280
import smbus2
import time


#retrieve and return single observation from BME280 (function called by WxStation Logger)
def retrieve_bme280_ob():
    bus, address = set_bme280_i2c()
    bme280.load_calibration_params(bus,address)
    return get_bme280_obs(bus,address) #pulls single set of obs, returns


#log BME280 T/q/P output to command line (1 second sampling frequency)
def log_bme280_to_cmd():
    bus, address = set_bme280_i2c()
    bme280.load_calibration_params(bus,address)

    while True:
        T,q,P = get_bme280_obs(bus,address)
        print(f"\r [+] Temperature: {T:5.2f} degC, Humidity: {q:5.2f} %, Pressure: {P:6.1f} mb", end=" ")
        time.sleep(1)


#return observation from calibrated BME280
def get_bme280_obs(bus,address):
    obs = bme280.sample(bus,address)

    q = obs.humidity
    P = obs.pressure
    T = obs.temperature
    
    return T,q,P


#configure I2C parameters for BME280
def set_bme280_i2c():
    port = 1 
    address = 0x77
    bus = smbus2.SMBus(port)
    
    return bus, address


#if function is called, run log to command line
if __name__ == "__main__":
    log_bme280_to_cmd()
