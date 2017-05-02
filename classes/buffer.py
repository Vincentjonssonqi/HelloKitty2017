import RPi.GPIO as GPIO
import time
import random


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

class Buffer:

    def __init__(self,pins,buffer_disable_pin,clock_pin,no_hardware):
        self.pins = pins or []
        self.size = len(self.pins)                                                                  #Buffer size means basically the number of pins, meaning number of bits that can be stored in the buffer
        self.no_hardware = no_hardware or False
        self.buffer_disable_pin = buffer_disable_pin
        self.clock_pin = clock_pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(self.buffer_disable_pin,GPIO.OUT)
        GPIO.setup(self.clock_pin,GPIO.OUT)

    #write-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description
    #Writes a integer value to the buffer


    #Parameters:
    #number: An integer number


    def write(self,number):
        GPIO.output(self.buffer_disable_pin,True)
        time.sleep(.1)

        buffer_values = self.convert_number_to_buffer(number)                                       #Generate buffer from the number
        for i in range(len(buffer_values)):                                                         #LOOP over buffer values
            pin_id = self.pins[i]                                                                   #fetch the pin id
            GPIO.setup(pin_id,GPIO.OUT)
        GPIO.output(self.clock_pin,True)
        time.sleep(.1)
        self.clock()                                                         #Set the current buffer pin to output mode
        for i in range(len(buffer_values)):
            GPIO.output(pin_id,buffer_values[i])
        print("WRITE OP value: {},code: {}".format(buffer_values,number))                                                    #Write buffer value to




    #read-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description
    #Reads the buffer and converts it to a number


    #Returns:
    #An integer number


    def read(self):
                                                            #Turn the the buffer chip on to be able to recieve stuff again
        buffer_values = []                                                                          #Generate buffer from the number
        for i in range(len(self.pins)):                                                             #LOOP over buffer values
            pin_id = self.pins[i]                                                                 	#fetch the pin id
            GPIO.setup(pin_id,GPIO.IN)
        time.sleep(.1)
        GPIO.output(self.buffer_disable_pin,False)                                                             #Set the current buffer pin to output mode

        for i in range(len(self.pins)):
            buffer_values.append(GPIO.input(pin_id))
        if self.no_hardware:
            time.sleep(random.randint(0,1))
            fake_value = random.randint(0,8)
            return None if fake_value > 2 else fake_value
        print(buffer_values)
        return self.convert_buffer_to_column(buffer_values)



    #convert_number_to_buffer-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description
    #Converts a integer value to an n bit binary number

    #Parameters:
    #number: An integer number that do not exceed the size of the buffer when converted into binary

    #Returns:
    #Buffer values in the form of a List<boolean>


    def clock (self):
        GPIO.output(self.clock_pin,False)
        GPIO.output(self.clock_pin,True)
        GPIO.output(self.clock_pin,False)
    def convert_number_to_buffer(self,number):


        if len(bin(number)) > self.size + 2:                                                      #Check if the input number exceeds buffer size
            raise ValueError("Number is to big for the buffer size")                                #Raise ValueError if number exceeds buffer size
        binary_string = bin(number).replace("0b","").zfill(self.size)                             #Convert the number into a binary string, remove unecessary prefix ("0b") and make sure the binary string is at least length = 3
        return [binary_string[i] == "1" for i in range(self.size)]                                #Convert binary string into boolean array






    #convert_number_to_buffer-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description
    #Converts a buffer array to an interger value

    #Parameters:
    #buffer: Array with boolean values indicating the values for each bit in the buffer

    #Returns:
    #Gives you an integer value back

    def convert_buffer_to_number(self,buffer):

        binary_string = ["1" if buffer[i] else "0" for i in range(len(buffer))]                     #Convert the buffer array into a binary string
        return int(binary_string,2)                                                                 #Convert binary string into Integer




	#convert_buffer_to_column-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description
    #Converts a buffer array to an column interger value

    #Parameters:
    #buffer: Array with boolean values indicating the values for each bit in the buffer

    #Returns:
    #Gives you an integer value back (either 0,1,2) or None if no column was active

    def convert_buffer_to_column(self,buffer):
        for i in range(len(buffer)):
            if not buffer[i]: return i
        return None
