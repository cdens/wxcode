#!/usr/bin/env python3

from time import sleep
from datetime import datetime
from os import remove, path
import sys, board, busio, digitalio, logging, threading
import sparkfun_qwiicas3935
import winddir
import webserverinteraction as web
import datetime as dt
import RPi.GPIO as GPIO

Logger = logging.getLogger(__name__)

def runLightningLogger():
    
    url = open("serveraddress","r").read().strip()
    currentLightningThread = LightningThread(url=url)
    currentLightningThread.start()
    
    

class LightningThread(threading.Thread):
    
    def __init__(self,config):
        
        super().__init__()
        
        GPIO.setmode(GPIO.BCM)
        
        self.change_config(config)
        self._locked = not bool(int(open("activelogging","r").read().strip()))
    
        #file to write to
        with open(".config") as c:
            lines = c.read().split("\n")
            self.password = lines[0].split(' ')[1]
            self.logfile = lines[1].split(' ')[1].strip()
            self.dateformat = lines[3].split(' ')[1].strip()
            
        #initializing lightning log
        if not self._locked:
            self.init_countfile()
            
        self.isConnected = False
        self.numAttempts = 0
        
        #for tracking whether to update server
        self.lastStrikeDate = dt.datetime(1,1,1)
    
        #thresholds
        self.maxAttempts = 20 #stop trying after 20 failed connects
        self.noise_floor = 3 
        self.watchdog_threshold = 3
    
        
    def init_countfile(self):
        if path.exists(self.logfile):
            remove(self.logfile)
        with open(self.logfile,"w") as f:
            f.write(datetime.strftime(datetime.utcnow(), self.dateformat) + "\n")
    
            
    def change_lock(self, status):
        self._locked = status
        
    def change_config(self, config):
        self.config = config
        self.password = self.config["password"]
        self.logfile = self.config["lightning"]
        self.dateformat = self.config["dateformat"]
        
        
    def attempt_connect(self):
        
        #accessing wind direction ADC first (don't know why this has to happen but it fixed the bug)
        Logger.debug("[+] Initializing wind direction")
        try:
            winddir.getwinddirection()
        except Exception as e:
            Logger.exception(e)
            
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
                Logger.info("[+] Lightning detector connected")
                self.isConnected = True
            else:
                self.numAttempts += 1
                Logger.debug(f"[-] Detector connect attempt {self.numAttempts} of {self.maxAttempts} failed")
                sleep(1)
            
    
        if not self.isConnected: #all connect attempts failed
            Logger.warning(f"[-] All detector connect attempts failed- terminating")
            sys.exit()
        
    
            
            
    def run(self):
        
        try:
            self.attempt_connect()
            
            #detector loop here
            while True:
                
                GPIO.setmode(GPIO.BCM)
                
                if not self._locked:
                    if self.interrupt.value:
                        itype = self.detector.read_interrupt_register()
            
                        if itype == self.detector.LIGHTNING:
                            dist = self.detector.distance_to_storm
                            energy = self.detector.lightning_energy
                            
                            if dist > 1 and energy > 0:
                                cdate = dt.datetime.utcnow()
                                cdtg = dt.datetime.strftime(cdate,self.dateformat)
                                with open(self.logfile,"a") as f:
                                    f.write(f"{cdtg},{dist},{energy}\n")
                                    
                                Logger.debug(f"[+] Lightning strike detected at {cdtg}, {dist} km away, energy={energy}")
                                
                                if (cdate - self.lastStrikeDate).total_seconds() > 60: #must be 1 minute since last update
                                    web.postlightningstrike(dist, cdtg, self.password, self.url)
                                    self.lastStrikeDate = cdate
            
                                self.detector.clear_statistics()
                        
                sleep(0.1)
                
        except KeyboardInterrupt:
            GPIO.cleanup()
        except Exception as e:
            Logger.exception(e)

            

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    runLightningLogger()
