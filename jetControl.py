from machine import Pin
import constants

class JetControl:

    PIN = Pin(constants.JET_PIN, Pin.OUT)

    def toggle_jet(self):
        JetControl.PIN.toggle()

    def jet_on(self):
        JetControl.PIN.on()

    def jet_off(self):
        JetControl.PIN.off()

    def is_jet_on(self):
        return JetControl.PIN.value() == 1