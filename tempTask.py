from tempControl import TempController
from lcdControl import LCD
from machine import Pin, SoftI2C
from utime import sleep

scl_pin = 15
sda_pin = 14
lcd = LCD(SoftI2C(scl=Pin(scl_pin), sda=Pin(sda_pin), freq=100000))
#lcd.puts("Hello, World!")

tc = TempController()

def temp_task():
    try:
        while True:
            #print("Blink task started.")
            tc.get_temperature()
            temp_str = "Temp: {:.2f} F".format(tc.current_temperature)
            lcd.puts(temp_str, y=3, x=0)
            sleep(5) # sleep 1sec
    except KeyboardInterrupt:
        return