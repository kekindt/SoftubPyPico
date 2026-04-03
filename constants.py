#from enum import Enum, IntEnum

class LedPins():
    JET_PIN = 18
    HEAT_PIN = 17
    LED_PIN = 16
    POWER_PIN = 0

class RelayPins():
    LED_RELAY_PIN = 12
    JET_RELAY_PIN = 13

SCL_PIN = 15
SDA_PIN = 14
LED_PIN = 12
JET_PIN = 13 #23
TEMP_PIN = 28

FAIL_SAFE_HOT = 110
FAIL_SAFE_COLD = 50 # 70
TARGET_TEMPERATURE = 65 # 103

MIN_TEMPERATURE = 90
MAX_TEMPERATURE = 105

class CycleTimes():
    TEMP_CHECK_TIME = 10 #60  # seconds
    JET_CHECK_TIME = 10    # seconds
    BLINK_CHECK_TIME = 1   # seconds
    QUEUE_CHECK_TIME = 0.5   # seconds
    CHECK_TARGET_TEMP_TIME = 1 # seconds

class TempCheckStatus():
    OFF = 0
    CIRCULATING = 1
    CHECKING = 2

class LcdLine():
    LINE1 = 0
    LINE2 = 1
    LINE3 = 2
    LINE4 = 3

class PanelButtonPins():
    JET = 19
    LIGHT = 6
    