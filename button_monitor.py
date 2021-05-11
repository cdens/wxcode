#! /usr/bin/env python3
# configures raspberry pi to listen to button hooked up to ground and GPIO pin to control Pi actions

import RPi.GPIO as GPIO
import time, subprocess
    

#function to listen for button press event
def button_press_event(button_num):
    
    global buttonStatus
    start_time = time.time()

    while GPIO.input(channel) == 0: # Wait for the button up
        pass

    buttonTime = time.time() - start_time    # How long was the button down?

    
    if buttomTime >= 6: #power off
        print("Shutting down")
        cmd = "sudo shutdown -h now"
        subprocess.run(cmd.split())
        
    elif buttonTime >= 3: #stop logging
        print("Terminating logging")
        with open("activelogging","w") as f:
            f.write("0")
        
    elif buttonTime >= .5: #start logging
        print("Starting logging")
        with open("activelogging","w") as f:
            f.write("1")
            

#main
if __name__ == "__main__":
        
    button_num = 16
    
    GPIO.add_event_detect(button_num, GPIO.FALLING, callback=button_press_event, bouncetime=500)