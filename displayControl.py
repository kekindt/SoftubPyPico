from collections import deque
from machine import UART
#import serial
#from jetControl import JetControl
#from lightControl import LightControl
#import time
import constants

class DisplayController:

    display_buffer = bytearray([0x02, 0x00, 0x01, 0x00, 0x00, 0x01, 0xFF])
    heat_on = False
    filter_on = False
    light_on = False
    queue: deque #= None
    
    def __init__(self):
        self.ser = UART(1, baudrate=constants.BAUDRATE, tx=constants.TX_PIN, rx=constants.RX_PIN) 
        
    def set_deque(self, queue: deque):
        self.queue = queue

    def set_leds(self, heat_on, filter_on):
        if heat_on and filter_on:
            DisplayController.display_buffer[constants.BufferPositions.LEDS] = 0x30
        elif heat_on and not filter_on:
            DisplayController.display_buffer[constants.BufferPositions.LEDS] = 0x20
        elif not heat_on and filter_on:
            DisplayController.display_buffer[constants.BufferPositions.LEDS] = 0x10
        else:
            DisplayController.display_buffer[constants.BufferPositions.LEDS] = 0x00

    def set_temperature(self, temperature):
        if temperature >= 100:
            DisplayController.display_buffer[constants.BufferPositions.TEMP1] = 1
        else:
            DisplayController.display_buffer[constants.BufferPositions.TEMP1] = 0x0A
        DisplayController.display_buffer[constants.BufferPositions.TEMP2] = (temperature // 10) % 10  
        DisplayController.display_buffer[constants.BufferPositions.TEMP3] = temperature % 10 

    def calculate_checksum(self, display_buffer):
        checksum = 0
        for i in range(1, len(display_buffer) - 2):
            checksum += display_buffer[i]
        checksum = checksum & 0xFF  
        display_buffer[constants.BufferPositions.CHECKSUM] = checksum

    def update_display(self):
        self.ser.write(bytearray(self.display_buffer))

    def receive_data(self):
        while True:
            if self.ser.any() > 0:
                bytes_received = self.ser.read(20)
                for byte in bytes_received if bytes_received is not None else []:
                    if (int(byte)) == constants.PanelButtons.JET:
                        DisplayController.queue.append('TOGGLE_JET')
                        self.set_leds(DisplayController.heat_on, DisplayController.filter_on)
                    elif (int(byte)) == constants.PanelButtons.LIGHT:
                        DisplayController.queue.append('TOGGLE_LIGHT')
                        self.set_leds(DisplayController.heat_on, DisplayController.filter_on)
                    elif (int(byte)) == constants.PanelButtons.UP:
                        DisplayController.queue.append('HEAT_UP')
                    elif (int(byte)) == constants.PanelButtons.DOWN:
                        DisplayController.queue.append('HEAT_DOWN')
                    elif (int(byte)) == constants.PanelButtons.NOISE:
                            pass # Ingore noise
                    

                
            

