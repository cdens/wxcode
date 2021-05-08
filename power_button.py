#! /usr/bin/env python3
# configures raspberry pi to listen to button hooked up to ground and GPIO pin (button_num) for button press event to shutdown

from gpiozero import Button
import threading, subprocess, os
    

#function to listen for button press event
def listen_for_shutdown(button_num):
    button = Button(button_num)
    button.wait_for_press()
    print("Shutting down")
    cmd = "sudo shutdown -h now"
    subprocess.run(cmd.split())
    
    
    

#main
if __name__ == "__main__":
        
    button_num = 16
    
    shutdown_thread = threading.Thread(target=listen_for_shutdown, args=(button_num,))
    shutdown_thread.start()