from machine import Pin
from utime import sleep

pin = Pin('LED', Pin.OUT)

def blink_task():
    try:
        while True:
            print("Blink task started.")
            pin.toggle()
            sleep(1) # sleep 1sec
    except KeyboardInterrupt:
        return