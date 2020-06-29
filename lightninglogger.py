#!/usr/bin/env python3

from time import sleep
import board
import busio
import digitalio
import sparkfun_qwiicas3935

#thresholds
noise_floor = 3 
watchdog_threshold = 3

#interrupt pin configuration
interrupt = digitalio.DigitalInOut(board.D24)
interrupt.direction = digitalio.Direction.INPUT
interrupt.pull = digitalio.Pull.DOWN

#SPI object
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

#chip select object setup
cs = digitalio.DigitalInOut(board.D23)
cs.direction = digitalio.Direction.OUTPUT

#create object for SPI comms with AS3935 detector
detector = sparkfun_qwiicas3935.Sparkfun_QwiicAS3935_SPI(spi, cs)
detector.noise_level = noise_floor #base level to filter out noise (higher = more exclusive)
detector.watchdog_threshold = watchdog_threshold #base level to filter out disturbers (higher = more exclusive)
detector.indoor_outdoor = detector.INDOOR #INDOOR or OUTDOOR mode


if detector.connected:
    print("Lightning detector connected")
else:
    print("Detector failed to connect")
    exit()

#detector loop here
while True:
    
    if interrupt.value:
        itype = detector.read_interrupt_register()

        #if itype == detector.NOISE:
        #    print("Noise")
        #elif itype == detector.DISTURBER:
        #    print("Disturber!")
        if itype == detector.LIGHTNING:
            dist = detector.distance_to_storm
            energy = detector.lightning_energy
            print(f"Lightning strike {dist} km away, energy={energy}")
            detector.clear_statistics()
        #else:
        #    print(f"Unknown type- {itype}")

    sleep(0.1)

