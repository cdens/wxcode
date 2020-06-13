#!/usr/bin/env python3

import bme280
import smbus2
import time


port = 1 
address = 0x77
bus = smbus2.SMBus(port)

bme280.load_calibration_params(bus,address)

while True:
    obs = bme280.sample(bus,address)

    q = obs.humidity
    P = obs.pressure
    T = obs.temperature

    print(f"\r [+] Temperature: {T:5.2f} degC, Humidity: {q:5.2f} %, Pressure: {P:6.1f} mb", end=" ")

    time.sleep(1)
