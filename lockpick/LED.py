import smbus

def LED(char):
    bus = smbus.SMBus(1)
    characters = [0xD5, 0x14, 0xB3, 0xB6, 0xD4, 0xE6, 0xC7, 0x34, 0xF7, 0xF4, 0x77, 0xF5]       #list of hex for characters [H, 0-9, A]
    if type(char) is int:
        bus.write_byte_data(0x54, 0x12, characters(char))
    elif char = "H":
        bus.write_byte_data(0x54, 0x12, characters(0))
    elif char = "A":
        bus.write_byte_data(0x54, 0x12, characters(9))
    else:
        raise ValueError
