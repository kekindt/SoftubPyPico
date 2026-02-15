#from displayControl import DisplayController
from machine import Pin, SoftI2C
from tempTask import temp_task

from utime import sleep
import threading
from lcdControl import LCD 

from blinkTask import blink_task



#pin = Pin(25, Pin.OUT)

print("LED starts flashing...")
#blink_thread = threading.Thread(target=temp_task)
#blink_thread.start()

#display = DisplayController()
#display_receive_thread = threading.Thread(target=display.receive_data)
#display_receive_thread.start()

# create temp thread 

temp_thread = threading.Thread(target=temp_task)
temp_thread.start()

while True:
    try:
        sleep(1)
    except KeyboardInterrupt:
        break


#pin.off()
print("Finished.")
