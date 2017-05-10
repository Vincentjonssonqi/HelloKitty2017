"""
brute
"""

import smbus
import time

def initialise():
    KEYPAD_KEYS = [["1","2","3"],["4","5","6"],["7","8","9"],["*","0","#"]]
    i2c = smbus.SMBus(1)
    i2c_addr = 0x38
    rows = [0x, 0x, 0x, 0x]
    columns = [0x, 0x, 0x]
def lockpick(lock_type="polling", pass_len=4):
    initialise()
    if (lock_type != "polling") and (lock_type != "interrupt"):
        raise ValueError("'polling' and 'interrupt' are the only valid lock types")
    password = ""
    for i in range(pass_len):
        for j in rows:
            for k in columns:       #row
                """
                if lock_type = "interrupt":
                    GPIO.output(k, False)
                    time.sleep(?)
                    GPIO.output(k, True)
                """
                last_val = None
                changed = False
                while not changed:
                    val = i2c.read_byte(0x38)
                    if last_val == None:
                        last_val = val
                    elif val != last_val:
                        changed = True
                i2c.write_byte(0x38, ?)





    return password
