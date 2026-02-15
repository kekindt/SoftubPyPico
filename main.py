#from asyncio import sleep
from displayControl import DisplayController
from tempControl import TempController
from lcdControl import LCD
from machine import Pin, SoftI2C
from utime import sleep
from onewire import OneWire
from collections import deque
import ds18x20
import constants
import threading

seconds = 0
heater_on = False
jets_on = False
hard_stop = False

queue = deque([], 10)

lcd = LCD(SoftI2C(scl=Pin(constants.SCL_PIN), sda=Pin(constants.SDA_PIN), freq=100000))

tempCheckTime = 5  # seconds
blinkCheckTime = 1  # seconds
jetCheckTime = 10  # seconds
queueCheckTime = 1 # seconds

tempCheckStatus = 0 # 0 - off, 1 - Circulating, 2 - Checking
tempCheckCycles = 0

lcd.puts("System Starting...", y=constants.LcdLine.LINE1, x=0)
sleep(2)

# Thread for Display control as we only have 2 threads and we need it to run 
# on it's own to pull serial data from the control panel
display = DisplayController()
display.set_deque(queue)
display_receive_thread = threading.Thread(target=display.receive_data)
display_receive_thread.start()

tc = TempController()
ow = OneWire(Pin(constants.TEMP_PIN)) # Need PIN Number
ds = ds18x20.DS18X20(ow)
t = ow.scan()[0]
ds.convert_temp()
sleep(0.75)
tt = ds.read_temp(t)

currentTemp = (tt * 9/5) + 32
temp_str = "Temp: {:.2f} F".format(currentTemp)
lcd.puts(temp_str, y=constants.LcdLine.LINE4, x=0)
#sleep(0.75)
#currentTemp = 0

blink_pin = Pin('LED', Pin.OUT)
led_pin = Pin(constants.LED_PIN, Pin.OUT)
jet_pin = Pin(constants.JET_PIN, Pin.OUT)
led_pin.on() # Turn off LED (Active Low)
jet_pin.on() # Turn off Jet (Active Low)

while True:
    # Simulating threads by Moding the second count to run tasks when needed like it was on a thread
    try:
        lcd.puts("System Running...", y=constants.LcdLine.LINE1, x=0)
        lcd.puts("Cycle Count: {}".format(seconds), y=constants.LcdLine.LINE2, x=0)
        if(seconds > 86400):  # reset every 24 hours, just so we don't eventually overflow
            seconds = 0 
            lcd.puts("System Cycle Reset", y=constants.LcdLine.LINE1, x=0)
        

        if seconds % constants.CycleTimes.TEMP_CHECK_TIME == 0:
            if tempCheckStatus == constants.TempCheckStatus.OFF:
                if tempCheckCycles == 0 or tempCheckCycles >= 3600:  # 1 hour
                    tempCheckStatus = constants.TempCheckStatus.CIRCULATING
                    lcd.puts("Circulating...", y=constants.LcdLine.LINE3, x=0)
                    tempCheckCycles = 0
                    queue.append('JETS_ON')
            elif tempCheckStatus == constants.TempCheckStatus.CIRCULATING:
                if tempCheckCycles >= 30:  # 5 minutes of circulation
                    tempCheckCycles = 0
                    tempCheckStatus = constants.TempCheckStatus.CHECKING
                    lcd.puts("Checking Temp...", y=constants.LcdLine.LINE3, x=0)
                    queue.append('JETS_OFF')
            elif tempCheckStatus == constants.TempCheckStatus.CHECKING:
                lcd.puts("                    ", y=constants.LcdLine.LINE3, x=0)
                tempCheckStatus = constants.TempCheckStatus.OFF
                tempCheckCycles = 0
                t = ow.scan()[0]
                ds.convert_temp()
                sleep(0.75)
                tt = ds.read_temp(t)

                currentTemp = (tt * 9/5) + 32
                temp_str = "Temp: {:.2f} F".format(currentTemp)
                lcd.puts(temp_str, y=constants.LcdLine.LINE4, x=0)
                display.set_temperature(int(currentTemp))
                display.update_display()
                if currentTemp > constants.FAIL_SAFE_HOT:
                    # past fail safe hot, shutdown heater
                    lcd.puts("WARNING: OVERHEAT!", y=constants.LcdLine.LINE1, x=0)
                    hard_stop = True
                    queue.append('HEATER_OFF')
                elif currentTemp < constants.FAIL_SAFE_COLD:
                    # past fail safe cold, turn on heater
                    lcd.puts("WARNING: TOO COLD!", y=constants.LcdLine.LINE1, x=0)
                    hard_stop = False
                    queue.append('HEATER_ON')
                elif currentTemp <= constants.TARGET_TEMPERATURE:
                    # turn on heater
                    hard_stop = False
                    lcd.puts("System Running...", y=constants.LcdLine.LINE1, x=0)  # clear warning
                    queue.append('HEATER_ON')
                elif currentTemp >= constants.TARGET_TEMPERATURE:
                    # turn off heater
                    hard_stop = False
                    lcd.puts("System Running...", y=constants.LcdLine.LINE1, x=0)  # clear warning
                    queue.append('HEATER_OFF')
                
        if seconds % constants.CycleTimes.BLINK_CHECK_TIME == 0:
            # Blink LED
            blink_pin.toggle()

        # if seconds % constants.CycleTimes.JET_CHECK_TIME == 0:
        #     # Toggle Jet
        #     jet_pin.toggle()

        if seconds % constants.CycleTimes.QUEUE_CHECK_TIME == 0:
            # Check Queue
            action = queue.popleft() if queue else None
            if action:
                if action == 'HEATER_ON':
                    heater_on = True
                elif action == 'HEATER_OFF':
                    heater_on = False
                elif action == 'JETS_ON':
                    jets_on = True
                elif action == 'JETS_OFF':
                    jets_on = False
                elif action == 'TOGGLE_JET':
                    jets_on = not jets_on
                elif action == 'LED_TOGGLE':
                    led_pin.toggle()
                elif action == 'TEMP_UP':
                    if constants.TARGET_TEMPERATURE + 1 < constants.FAIL_SAFE_HOT:
                        constants.TARGET_TEMPERATURE += 1
                elif action == 'TEMP_DOWN':
                    if constants.TARGET_TEMPERATURE - 1 > constants.FAIL_SAFE_COLD:
                        constants.TARGET_TEMPERATURE -= 1

            if (heater_on or jets_on) and not hard_stop:
                jet_pin.off() # Active Low
            elif (not heater_on and not jets_on and tempCheckStatus != constants.TempCheckStatus.CIRCULATING) or hard_stop:
                jet_pin.on() # Active Low
            
            display.set_leds(heater_on, jets_on)
            display.update_display()

        seconds += 1
        tempCheckCycles += 1
        sleep(1)
    except KeyboardInterrupt:
        break