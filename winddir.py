#!/usr/bin/env python3

from gpiozero import MCP3008
import time
import RPi.GPIO as GPIO

Vref = 3.3

#GPIO.setmode(GPIO.BOARD)
#clk = 23 
#mosi = 19
#miso = 21

GPIO.setmode(GPIO.BCM)
clk = 11
miso = 9
mosi = 10
cs = 22

GPIO.setup(cs, GPIO.IN)

results = []
for ch in range(0,8):
    results.append( MCP3008(channel=ch, clock_pin=clk, mosi_pin=mosi, miso_pin=miso))
    print(f"Channel {ch}: Value= {results[ch].value*Vref} V")

#ch = 0
#m = MCP3008(channel=ch, clock_pin=clk, miso_pin=miso, mosi_pin=mosi)
#m = MCP3008(channel=ch)
#print(m.value)

#GPIO.cleanup()
