#!/usr/bin/env python3

import busio, digitalio, board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import numpy as np
import RPi.GPIO as GPIO



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
    
    
    
def print_voltages(channels):
    
    #print output from channels
    for (i,ch) in enumerate(channels):
        print(f"Channel {i}: value={ch.value}, voltage={ch.voltage}")

        
        
#get wind direction when multiple switches are triggered simultaneously
def getdirfrommultigoodvals(isvalid, dirs):
    
    ii = 0
    seqs = []
    seqs[0] = [isvalid[0]]
    
    #parsing indices into lists of consecutive values (e.g. [1,2,5,6,7] => [[1,2],[5,6,7]])
    for i in isvalid[1:]:
        if i == seqs[ii][-1] + 1:
            seqs[ii].append(i)
        else:
            ii += 1
            seqs.append([i])
            
    #finding longest consecutive sequence
    seqlens = []
    for clist in seqs:
        seqlens.append(len(clist))
    mainseq = seqs[np.argmax(seqlens)]
    
    
    ld = len(dirs)
    if not (ld-1 in isvalid and 0 in isvalid): #if channels with high voltages don't cross over 360->0
        winddir = np.mean(dirs[mainseq])
        
    else:
        
        #pull lists with start and end indices
        maxlen = np.max(seqlens)
        for s in seqs:
            if ld-1 in s:
                sE = s
            elif 0 in s:
                sS = s
        
        if len(sE) + len(sS) > maxlen: #use new sequences 
            sS += 360
            winddir = np.mean(dirs[sS + sE])
            if winddir >= 360:
               winddir -= 360 
        
        else:
            winddir = np.mean(dirs[mainseq])
            
        
    return winddir
        
    
    
        

# gets wind direction using threshold where 
def get_winddir_from_voltages(channels, threshold):
    
    winddir = -1
    dirs = np.array([0, 45, 90, 135, 180, 225, 270, 315])
    
    winddir = dirs[np.argmax(channels)]
    
    return winddir
    
    
    
def getwinddirection():
    channels = get_channel_values()
    chvoltages = []
    for ch in channels:
        chvoltages.append(ch.voltage)
    chvoltages = np.asarray(chvoltages)
    winddir = get_winddir_from_voltages(chvoltages, 0.8)
    
    if winddir == -1:
        winddir = 0
        
    return winddir
    
    
if __name__ == "__main__":
    channels = get_channel_values()
    print_voltages(channels)
    
    
