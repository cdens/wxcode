#! /usr/bin/env python3
# configures raspberry pi to listen to button hooked up to ground and GPIO pin to control Pi actions
    
import time, threading, logging
import RPi.GPIO as GPIO

Logger = logging.getLogger(__name__)

class ButtonThread(threading.Thread):
    
    def __init__(self):
        super().__init__()
        
        self.button_num = 16
        self._status = 0
        self._locked = False
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.button_num, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        
    def change_lock(self,lockStatus):
        self._locked = lockStatus
        
    def change_status(self,status):
        self._status = status
        
    def change_config(self,config):
        pass #this method is useless but simplifies the looping to update thread configurations in runWeatherStation.py
        
    def get_status(self):
        return self._status
        
    def run(self):
        
        try:
            while True:
                if not self._locked:
                    GPIO.wait_for_edge(self.button_num, GPIO.FALLING)
                    
                    start = time.time()
                    time.sleep(0.2) #allowing voltage to drop
                
                    while GPIO.input(self.button_num) == GPIO.LOW: #waiting for button release
                        time.sleep(0.01)
                        
                    buttonTime = time.time() - start #getting button press duration
                    
                    #duration   status  action
                    #0.3-2.9    1 or 2  start wxlogger if inactive or log current conditions if logger is active
                    #3-5.9      3       stop wxlogger
                    #6+         4       shutdown raspberry pi
                    
                    if buttonTime >= 6: #power off
                        self.change_status(4)
                    elif buttonTime >= 3: #stop logging
                        self.change_status(3)
                    elif buttonTime >= .3: #start logging
                        if int(open("activelogging","r").read().strip()):
                            self.change_status(2)
                        else:
                            self.change_status(1)
                        
                        
        except KeyboardInterrupt:    
            GPIO.cleanup()
        except Exception as e:
            Logger.exception(e)
            
            
if __name__ == "__main__":
    BT = ButtonThread()
    BT.start()