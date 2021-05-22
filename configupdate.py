#!/usr/bin/env python3 

import time, threading, logging
from os import remove, path
from hashlib import sha1

Logger = logging.getLogger(__name__)


class ConfigThread(threading.Thread):
    
    def __init__(self, configfile):
        
        super().__init__()
        
        self.filename = configfile
        self.options = ["password", "lightning", "rain", "dateformat", "gps", "gpsbaud", "url"]
        self.file_hash = ""
        self.config = None
        self.update_config()
        self._updated = False
        
        with open(".config") as c:
            lines = c.read().split("\n")
            self.logfile = lines[2].split(' ')[1].strip()
            self.dateformat = lines[3].split(' ')[1].strip()
                
        
    def get_status(self):
        return self._updated
        
    def set_status(self,status):
        self._updated = status
    
    def update_config(self):
        newconfig = {}
        with open(self.filename) as c:
            lines = c.read().split("\n")
            for line in lines:
                cdata = line.split(' ')
                key = cdata[0].lower()
                value = cdata[1]
                if key in options:
                    newconfig[key] = value
                else:
                    Logger.warning(f"[!] Invalid key {key} with value {value} provided in config file!")
        self.config = newconfig
        self.set_status(True)
        self.update_file_hash()
        
        
    def get_hash(self,filename):
        return sha1(filename.encode('utf-8')).hexdigest()
        
        
    def run(self):
        try:
            while True:
                if self.file_hash != self.get_hash(self.filename):
                    self.update_config()
                time.sleep(30)  #takes 30 seconds to update config file
                
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            Logger.exception(e)
    
    
    
if __name__ == "__main__":
    runRainLogger()
    