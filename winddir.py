#!/usr/bin/env python3

import busio, digitalio, board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

#create SPI interface
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

#create chip select instance
cs = digitalio.DigitalInOut(board.D22)

#create MCP3008 instance
mcp = MCP.MCP3008(spi, cs)

#create analog input channels
channels = []
mcp_pins = [MCP.P0, MCP.P1, MCP.P2, MCP.P3, MCP.P4, MCP.P5, MCP.P6, MCP.P7]
for ch in range(8):
    channels.append(AnalogIn(mcp, mcp_pins[ch]))


#print output from channels
for (i,ch) in enumerate(channels):
    print(f"Channel {i}: value={ch.value}, voltage={ch.voltage}")
