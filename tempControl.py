import constants
import machine
import onewire
import ds18x20

class TempController:
    target_temperature = constants.TARGET_TEMPERATURE  # Default target temperature
    current_temperature = 0.0

    @classmethod
    def set_target_temperature(cls, temperature):
        cls.target_temperature = temperature

    @classmethod
    def get_target_temperature(cls):
        return cls.target_temperature
    
    @classmethod
    def get_temperature(cls):
        ow = onewire.OneWire(machine.Pin(28)) # Need PIN Number
        ds = ds18x20.DS18X20(ow)
        t = ow.scan()[0]
        cls.current_temperature = (ds.read_temp(t) * 9/5) + 32 

    # Need temp monitor task for Threading