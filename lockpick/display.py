import smbus
import time


class Display:
        def __init__(self):
                #dict of hex for characters [0-9, A, H]
                self.characters = {"0": 0xEE, "1": 0x28, "2": 0xCD, "3": 0x6D, "4": 0x2B, "5": 0x67, "6": 0xE7, "7": 0x2C, "8": 0xEF, "9": 0x6F, "#": 0xAB, "*": 0xAF}
                self.bus = smbus.SMBus(1)
                self.bus.write_byte_data(0x24, 0x03, 0x00)

        def show(self, char):
                self.bus.write_byte_data(0x24, 0x01, self.characters[char])
