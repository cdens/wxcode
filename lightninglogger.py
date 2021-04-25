#!/usr/bin/env python3

from time import sleep
import threading

import sys
import board
import busio
import digitalio
import sparkfun_qwiicas3935
import webserverinteraction as web
import datetime as dt
import RPi.GPIO as GPIO



def runLightningLogger():
    
    currentLightningThread = LightningThread()
    currentLightningThread.start()
    

        

class LightningThread(threading.Thread):
    
    def __init__(self):
        
        super().__init__()
        
        GPIO.setmode(GPIO.BCM)
        
        self.locked = False
    
        #file to write to
        with open(".config") as c:
            lines = c.read().split("\n")
            logfile = lines[1].split(' ')[1].strip()
            dateformat = lines[3].split(' ')[1].strip()
            
        #initializing lightning log
        with open(logfile,"w") as f:
            f.write(dt.datetime.strftime(dt.datetime.utcnow(), dateformat) + "\n")
            
        self.isConnected = False
        self.numAttempts = 0
    
        #thresholds
        self.maxAttempts = 20 #stop trying after 20 failed connects
        self.noise_floor = 3 
        self.watchdog_threshold = 3
        
    
    def change_lock(self, status):
        self.locked = status
        
        
    def attempt_connect(self):
        
        while not self.isConnected and self.numAttempts < self.maxAttempts:

            #interrupt pin configuration
            self.interrupt = digitalio.DigitalInOut(board.D24)
            self.interrupt.direction = digitalio.Direction.INPUT
            self.interrupt.pull = digitalio.Pull.DOWN
        
            #SPI object
            self.spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        
            #chip select object setup
            self.cs = digitalio.DigitalInOut(board.D23)
            self.cs.direction = digitalio.Direction.OUTPUT
        
            #create object for SPI comms with AS3935 detector
            self.detector = sparkfun_qwiicas3935.Sparkfun_QwiicAS3935_SPI(self.spi, self.cs)
            self.detector.noise_level = self.noise_floor #base level to filter out noise (higher = more exclusive)
            self.detector.watchdog_threshold = self.watchdog_threshold #base level to filter out disturbers (higher = more exclusive)
            self.detector.indoor_outdoor = self.detector.INDOOR #INDOOR or OUTDOOR mode
            
                
            #checking whether receiver is communicating properly- terminating if not
            if self.detector.connected:
                print("[+] Lightning detector connected")
                self.isConnected = True
            else:
                self.numAttempts += 1
                print(f"[-] Detector connect attempt {self.numAttempts} of {self.maxAttempts} failed")
                sleep(1)
            
    
        if not self.isConnected: #all connect attempts failed
            print(f"[-] All detector connect attempts failed- terminating")
            sys.exit()
        
    
            
            
    def run(self):
        
        self.attempt_connect()
        
        #detector loop here
        while True:
            
            GPIO.setmode(GPIO.BCM)
            
            if not self.locked:
                if self.interrupt.value:
                    itype = self.detector.read_interrupt_register()
        
                    if itype == self.detector.LIGHTNING:
                        dist = self.detector.distance_to_storm
                        energy = self.detector.lightning_energy
                        
                        if dist > 1 and energy > 0:
                            with open(logfile,"a") as f:
                                f.write(f"{dist},{energy}\n")
                            print(f"[+] Lightning strike detected at {dt.datetime.strftime(dt.datetime.utcnow(),dateformat)}, {dist} km away, energy={energy}")
                            web.postlightningstrike(dist,energy)
        
                            self.detector.clear_statistics()
                    
    
            sleep(0.1)

            

if __name__ == "__main__":
    runLightningLogger()
