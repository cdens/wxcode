#!/usr/bin/env python3

import busio, digitalio, board, logging
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import numpy as np
import RPi.GPIO as GPIO

Logger = logging.getLogger(__name__)


def get_channel_values():
    
    GPIO.setmode(GPIO.BCM)
    
    
    #create SPI interface
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    
    #create chip select instance
    cs = digitalio.DigitalInOut(board.D22)
    
    #create MCP3008 instance
    mcp = MCP.MCP3008(spi, cs)
    
    #create analog input channels
    channels = []
    mcp_pins = [MCP.P0, MCP.P1, MCP.P2, MCP.P3, MCP.P4, MCP.P5, MCP.P6, MCP.P7]
    for pin in mcp_pins:
        channels.append(AnalogIn(mcp, pin))
        
    return channels
    

        
    
def get_winddir_from_voltages(channels):
    
    winddir = -1
    dirs = np.array([0., 45., 90., 135., 180., 225., 270., 315.])
    dirs *= np.pi/180 #convert to radians

    winddir = np.arctan2(np.sin(np.nansum(dirs * channels)), np.cos(np.nansum(dirs * channels)))
    winddir *= 180/np.pi #convert to degrees

    if winddir <= 0:
        winddir +=360
    
    return winddir
    
    
    
def getwinddirection():
    channels = get_channel_values()
    chvoltages = []
    chvoltstr = "WDir Voltages: "
    for i,ch in enumerate(channels):
        chvoltages.append(ch.voltage)
        chvoltstr += f"CH:{i}={ch.voltage:3.2f}V, "
    chvoltages = np.asarray(chvoltages)
    
    Logger.debug(chvoltstr)
    print(chvoltstr)
        
        
    
    winddir = get_winddir_from_voltages(chvoltages)
    
    if winddir == -1:
        winddir = 0
        
    return winddir
    
    
if __name__ == "__main__":
    channels = get_channel_values()
    #print_voltages(channels)
    #print(channels)
    winddir = getwinddirection()
    print(winddir)
    
    
