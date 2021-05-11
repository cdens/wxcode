#! /usr/bin/env python3
# configures raspberry pi to listen to button hooked up to ground and GPIO pin to control Pi actions

# import RPi.GPIO as GPIO
# import time, subprocess
    

#function to listen for button press event
# def button_press_event(button_num):
    
#     start_time = time.time()
    
#     print("Starting loop at" + str(start_time))
#     while GPIO.input(button_num) == 0: # Wait for the button up
#         pass

#     buttonTime = time.time() - start_time    # How long was the button down?

    
#     if buttonTime >= 6: #power off
#         print("Shutting down")
#         cmd = "sudo shutdown -h now"
#         subprocess.run(cmd.split())
        
#     elif buttonTime >= 3: #stop logging
#         print("Terminating logging")
#         with open("activelogging","w") as f:
#             f.write("0")
        
#     elif buttonTime >= .5: #start logging
#         print("Starting logging")
#         with open("activelogging","w") as f:
#             f.write("1")
            

# #main
# if __name__ == "__main__":
        
#     button_num = 16
    
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(button_num, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#     GPIO.add_event_detect(button_num, GPIO.FALLING, callback=button_press_event, bouncetime=500)
    
#     while True:
#         time.sleep(10)
        
#     GPIO.cleanup()
    
    
import time, subprocess
import RPi.GPIO as GPIO

button_num = 16

GPIO.setmode(GPIO.BCM)
GPIO.setup(button_num, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    GPIO.wait_for_edge(PIN, GPIO.FALLING)
    
    
    start = time.time()
    time.sleep(0.2)

    while GPIO.input(PIN) == GPIO.LOW:
        time.sleep(0.01)
        
    buttomTime = time.time() - start
    
    if buttonTime >= 6: #power off
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
        

GPIO.cleanup()