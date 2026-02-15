from machine import Pin
import constants

class LightControl:
    PIN = Pin(constants.LED_PIN, Pin.OUT)

    def toggle_light(self):
        LightControl.PIN.toggle()

    def light_on(self):
        LightControl.PIN.on()

    def light_off(self):
        LightControl.PIN.off()  

    def is_light_on(self):
        return LightControl.PIN.value() == 1