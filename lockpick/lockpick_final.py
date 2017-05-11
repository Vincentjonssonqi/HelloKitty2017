import smbus
import time

i2c = smbus.SMBus(1)
i2c.write_byte(0x38, 0xFF)

KEYPAD_KEYS = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["#", "0", "*"]]

def press(column):
    columns = [0b11110011, 0b11110101, 0b11111001]
    i2c.write_byte(0x38, columns[column])

def unpress():
    i2c.write_byte(0x38, 0b11110001)
unpress()
def wait(val):
	bit_patterns = [0b11100001, 0b11010001, 0b10110001, 0b01110001, 0b11110001]
	value = i2c.read_byte(0x38)
	print(value)
	while i2c.read_byte(0x38) != bit_patterns[val]:
		pass

def test(column, row):
	x = time.time()
	press(column)
	time.sleep(0.005)
	unpress()
	wait(row)
	press(column)
	time.sleep(0.005)
	unpress()
	wait(4)
	if (time.time()-x) < 0.018:
		print(time.time()-x)
		print("correct")


def test_correct():
	test(0,0)
	time.sleep(0.2)
	test(1,0)
	time.sleep(0.2)
	test(2,0)
	time.sleep(0.2)
	test(0,1)
