import smbus
import time

bus = smbus.SMBus(1)

bus.write_byte(0x38, 0xFF)
