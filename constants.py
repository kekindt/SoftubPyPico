#from enum import Enum, IntEnum

SCL_PIN = 15
SDA_PIN = 14
LED_PIN = 12
JET_PIN = 13#23
TEMP_PIN = 28

TX_PIN = 4
RX_PIN = 5

FAIL_SAFE_HOT = 110
FAIL_SAFE_COLD = 50 # 70
TARGET_TEMPERATURE = 65 # 103
SERIAL_PORT = '/dev/serial0'
BAUDRATE = 2400
TIMEOUT = 1

class CycleTimes():
    TEMP_CHECK_TIME = 60  # seconds
    JET_CHECK_TIME = 10    # seconds
    BLINK_CHECK_TIME = 1   # seconds
    QUEUE_CHECK_TIME = 0.5   # seconds

class TempCheckStatus():
    OFF = 0
    CIRCULATING = 1
    CHECKING = 2

class LcdLine():
    LINE1 = 0
    LINE2 = 1
    LINE3 = 2
    LINE4 = 3

class BufferPositions():
    HEADER = 0
    LEDS = 1
    TEMP1 = 2
    TEMP2 = 3
    TEMP3 = 4
    CHECKSUM = 5
    TRAILER = 6

class PanelButtons():
    JET = 30
    LIGHT = 45
    UP = 75
    DOWN = 135
    NOISE = 15