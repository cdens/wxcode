#!/usr/bin/env python3

from picamera import PiCamera
import time
from datetime import datetime

global camera
camera = PiCamera()

def takeimage(filename):
    global camera
    
    camera.start_preview() #camera on
    time.sleep(4) #allow sensors to focus camera
    camera.capture(filename) #take/save picture
    camera.stop_preview() #camera off


def runtimelapse(numpics,interval):
    
    estruntime = 4  #each picture takes about 6 seconds to run
    if interval < 10:
        interval = 10 

    fileheader = "../Pictures/image"
    imageformat = ".jpg"

    for p in range(numpics):
        cdtstr = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        takeimage(fileheader + cdtstr + imageformat)
        time.sleep(interval - estruntime)
