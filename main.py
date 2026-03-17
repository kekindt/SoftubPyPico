#from asyncio import sleep
#from displayControl import DisplayController
from tempControl import TempController
from lcdControl import LCD
from machine import ADC, Pin, SoftI2C
from utime import sleep, time
from onewire import OneWire
from collections import deque
import ds18x20
import constants
import threading

seconds = 0
heater_on = False
jets_on = False
light_on = False
hard_stop = False

queue = deque([], 10)
currentTemp = 50
light_last = time() * 1000

lcd = LCD(SoftI2C(scl=Pin(constants.SCL_PIN), sda=Pin(constants.SDA_PIN), freq=100000))

tempCheckTime = 5  # seconds
blinkCheckTime = 1  # seconds
jetCheckTime = 10  # seconds
queueCheckTime = 1 # seconds

tempCheckStatus = 0 # 0 - off, 1 - Circulating, 2 - Checking
tempCheckCycles = 0

lcd.puts("System Starting...", y=constants.LcdLine.LINE1, x=0)
sleep(1)

blink_pin = Pin('LED', Pin.OUT)
led_relay_pin = Pin(constants.RelayPins.LED_RELAY_PIN, Pin.OUT)
jet_relay_pin = Pin(constants.RelayPins.JET_RELAY_PIN, Pin.OUT)
led_relay_pin.on() # Turn off LED (Active Low)
jet_relay_pin.on() # Turn off Jet (Active Low)

light_led_pin = Pin(constants.LedPins.LED_PIN, Pin.OUT)
jet_led_pin = Pin(constants.LedPins.JET_PIN, Pin.OUT)
heat_led_pin = Pin(constants.LedPins.HEAT_PIN, Pin.OUT)

light_led_pin.off() # Active Low
jet_led_pin.on() # Active Low

pot = ADC(Pin(27)) # Potentiometer for temperature control, needs pin number

light_button = Pin(constants.PanelButtonPins.LIGHT, Pin.IN, Pin.PULL_DOWN)
jet_button = Pin(constants.PanelButtonPins.JET, Pin.IN, Pin.PULL_DOWN)
   
#tc = TempController()
ow = OneWire(Pin(constants.TEMP_PIN)) # Need PIN Number
ds = ds18x20.DS18X20(ow)
t = ow.scan()[0]
ds.convert_temp()
sleep(0.75)
tt = ds.read_temp(t)

currentTemp = (tt * 9/5) + 32 # Convert to Fahrenheit
temp_str = "Temp: {:.2f} F".format(currentTemp)
lcd.puts(temp_str, y=constants.LcdLine.LINE4, x=0)

def button_handler( pin):
    if pin is light_button:
        now = time() * 1000
        if (now - light_last) > 500:
            print("Toggling LED")
            led_relay_pin.toggle()
            light_led_pin.toggle() 
            lcd.puts("LEDs: {}    ".format(light_led_pin.value() == 1), y=constants.LcdLine.LINE2, x=0)
    elif pin is jet_button:
        now = time() * 1000
        if (now - light_last) > 500:
            print("Toggling Jet")
            jet_relay_pin.toggle()
            jet_led_pin.toggle()
            lcd.puts("Jets: {}    ".format(jet_led_pin.value() == 1), y=constants.LcdLine.LINE2, x=0)

def set_leds(heat_on, jet_on, light_on):
    if heat_on:
        heat_led_pin.on() # Active Low
    else:
        heat_led_pin.off()
    if jet_on:
        jet_led_pin.off() # Active Low
    else:
        jet_led_pin.on()

def get_target_temperature(_currentTemp):
    pot_value = pot.read_u16() # read value, 0-65535 across voltage range 0.0v - 3.3v
    print("Pot Value: ", pot_value)
    # Map pot_value to a temperature range (e.g., 50°F to 110°F)
    temp = constants.MIN_TEMPERATURE + (pot_value / 4300)
    temp = round(temp)
    print("Mapped Temp: ", temp)
    if( temp < constants.MIN_TEMPERATURE):
        temp = constants.MIN_TEMPERATURE
    elif( temp > constants.MAX_TEMPERATURE):
        temp = constants.MAX_TEMPERATURE

    if(temp > constants.FAIL_SAFE_HOT or temp < constants.FAIL_SAFE_COLD):
        # If the new temp is outside of the fail safe range compared to current temp, ignore it
        return

    if(temp < _currentTemp):
        queue.append('SET_TARGET_TEMP')
    elif(temp > _currentTemp):
        queue.append('SET_TARGET_TEMP')

    temp_str = "CT:{:.2f} : TT:{:.2f}".format(currentTemp, constants.TARGET_TEMPERATURE)
    lcd.puts(temp_str, y=constants.LcdLine.LINE4, x=0)

    return temp 

light_button.irq(trigger=Pin.IRQ_RISING, handler=button_handler) 

while True:
    # Simulating threads by Moding the second count to run tasks when needed like it was on a thread
    try:
        lcd.puts("Status: ", y=constants.LcdLine.LINE1, x=0)
        lcd.puts("Running", y=constants.LcdLine.LINE1, x=8)
        # lcd.puts("LEDs: {}".format(light_on), y=constants.LcdLine.LINE2, x=0)
        
        if(seconds > 86400):  # reset every 24 hours, just so we don't eventually overflow
            seconds = 0 
            lcd.puts("System Cycle Reset", y=constants.LcdLine.LINE1, x=0)

        if seconds % constants.CycleTimes.TEMP_CHECK_TIME == 0:
            if tempCheckStatus == constants.TempCheckStatus.OFF:
                if tempCheckCycles == 0 or tempCheckCycles >= 3600:  # 1 hour
                    tempCheckStatus = constants.TempCheckStatus.CIRCULATING
                    lcd.puts("Circulating", y=constants.LcdLine.LINE3, x=0)
                    tempCheckCycles = 0
                    queue.append('JETS_ON')
            elif tempCheckStatus == constants.TempCheckStatus.CIRCULATING:
                if tempCheckCycles >= 30:  # 5 minutes of circulation
                    tempCheckCycles = 0
                    tempCheckStatus = constants.TempCheckStatus.CHECKING
                    lcd.puts("Checking Temp", y=constants.LcdLine.LINE3, x=0)
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
                temp_str = "CT:{:.2f}F : TT:{:.2f}F".format(currentTemp, constants.TARGET_TEMPERATURE)
                lcd.puts(temp_str, y=constants.LcdLine.LINE4, x=0)
                
                
                if currentTemp > constants.FAIL_SAFE_HOT:
                    # past fail safe hot, shutdown heater
                    lcd.puts("OVERHEAT!", y=constants.LcdLine.LINE1, x=8)
                    hard_stop = True
                    queue.append('HEATER_OFF')
                elif currentTemp < constants.FAIL_SAFE_COLD:
                    # past fail safe cold, turn on heater
                    lcd.puts("Too Cold!", y=constants.LcdLine.LINE1, x=8)
                    hard_stop = False
                    queue.append('HEATER_ON')
                elif currentTemp <= constants.TARGET_TEMPERATURE:
                    # turn on heater
                    hard_stop = False
                    lcd.puts("Running", y=constants.LcdLine.LINE1, x=8)  # clear warning
                    queue.append('HEATER_ON')
                elif currentTemp >= constants.TARGET_TEMPERATURE:
                    # turn off heater
                    hard_stop = False
                    lcd.puts("Running", y=constants.LcdLine.LINE1, x=8)  # clear warning
                    queue.append('HEATER_OFF')
                
        if seconds % constants.CycleTimes.BLINK_CHECK_TIME == 0:
            # Blink LED
            blink_pin.toggle()
            

        if seconds % constants.CycleTimes.CHECK_TARGET_TEMP_TIME == 0:
             # Toggle Jet
             constants.TARGET_TEMPERATURE = get_target_temperature(currentTemp)

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

            if (heater_on or jets_on) and not hard_stop:
                jet_relay_pin.off() # Active Low
            elif (not heater_on and not jets_on and tempCheckStatus != constants.TempCheckStatus.CIRCULATING) or hard_stop:
                jet_relay_pin.on() # Active Low
            
        seconds += 1
        tempCheckCycles += 1
        sleep(1)
    except KeyboardInterrupt:
        break