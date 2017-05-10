import smbus
import time

i2c = smbus.SMBus(1)
i2c.write_byte(0x38, 0xFF)

for i in range(1):
	x=time.time()
	time.sleep(1)
	print(time.time()-x)

password = []
correct = False
while True:

    last_val = None
    changed = False
    x = time.time()
    while not changed:
        val = i2c.read_byte(0x38)
        if last_val == None:
            last_val = val
        elif val != last_val:
            changed = True
            print(val)
    if (correct == True) and (val == 1):
        password.append(last_val)
        print(password)
        correct = False
    delay = time.time()-x
    if (len(password) == 3) and (2.5 > delay > 2):
        correct = True

    if (0.3 > delay > 0.1):
        correct = True
        print(val, "correct")
    if delay>0.1:
        print(delay)
def interrupt():
    for i in []
