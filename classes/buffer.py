import RPi.GPIO as GPIO
import time
import random
from threading import Timer
class Buffer:

    def __init__(self,pins,buffer_control_pin,register_control_pin,column_change_pin,neutral_command,interrupt_command,no_hardware):
        self.pins = pins or []
        #Buffer size means basically the number of pins, meaning number of bits that can be stored in the buffer
        self.size = len(self.pins)

        self.neutral_command = neutral_command
        self.interrupt_command = interrupt_command

        self.no_hardware = no_hardware or False
        self.buffer_control_pin = buffer_control_pin
        self.register_control_pin = register_control_pin
        self.column_change_pin = column_change_pin



        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.column_change_pin,GPIO.IN)
        GPIO.setup(self.buffer_control_pin,GPIO.OUT)
        GPIO.setup(self.register_control_pin,GPIO.OUT)



    #start_keypad_interupt

    #Description:
    #Asks the pi to call the poll_keypad function when an active column is detected
    #The difference between this and constantly polling is that you save a lot of resources when you
    #only have to poll the keypad when a person is actually pressing a key
    def next_column_change(self):
        #We start of by writing switching the keypad state to interupt mode
        self.write(self.interrupt_command)
        time.sleep(.001)
        #This basically mean that we ensure that we drive a 0 onto all rows at the same time always
        #At least until we detect a key press
        #When that happens the interupt should be triggered and we perform the same polling as before
        #The advantage of this is that we do not poll all the time, only when the user is actually
        #interacting with the keypad
        try:
            if self.no_hardware:
                time.sleep(random.randint(0,1))
                return
            GPIO.wait_for_edge(self.column_change_pin, GPIO.FALLING)
            return
        except KeyboardInterrupt:
            GPIO.cleanup()



    #write-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description
    #Writes a integer value to the buffer


    #Parameters:
    #number: An integerself.buffer.neutral_commandfer(False)
    def write(self,number):
        self.enable_buffer(False)
        time.sleep(.001)
        #Generate buffer from the number
        buffer_values = self.convert_number_to_buffer(number)
        #LOOP over buffer values
        for i in range(len(self.pins)):
            #fetch the pin id
            pin_id = self.pins[i]
            #Set the current buffer pin to output mode and set these pins to their corresponding value
            GPIO.setup(pin_id,GPIO.OUT)
            GPIO.output(pin_id,buffer_values[i])
        #print("WRITE OP value: {},code: {}".format(buffer_values,number))
        time.sleep(.001)
        self.clock_register()






    #read-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description
    #Reads the buffer and converts it to a number


    #Returns:
    #An integer number


    def read(self):
        #Turn the register chip off so that you do not have interference
        self.enable_register(False)
        time.sleep(.001)

        #Generate buffer from the number
        buffer_values = []
        #LOOP over buffer values
        for i in range(len(self.pins)):
            #fetch the pin id
            pin_id = self.pins[i]
            GPIO.setup(pin_id,GPIO.IN)

        self.enable_buffer(True)
        time.sleep(.001)

        for i in range(len(self.pins)):
            pin_id = self.pins[i]
            buffer_values.append(GPIO.input(pin_id))




        if self.no_hardware:
            time.sleep(random.randint(0,3))
            fake_value = random.randint(0,8)
            return None if fake_value > 2 else fake_value

        #print("READ: {}".format(buffer_values))
        return self.convert_buffer_to_column(buffer_values)




    def enable_buffer(self,enable):
        #print("enable buffer: {} pin: {}".format(enable,self.buffer_control_pin))
        GPIO.output(self.buffer_control_pin,not enable)
    def enable_register(self,enable):
        #print("enable register: {} pin: {}".format(enable,self.register_control_pin))
        GPIO.output(self.register_control_pin,enable)

    #convert_number_to_buffer-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description
    #Converts a integer value to an n bit binary number

    #Parameters:
    #number: An integer number that do not exceed the size of the buffer when converted into binary

    #Returns:
    #Buffer values in the form of a List<boolean>


    def clock_register (self):
        self.enable_register(False)
        time.sleep(.001)
        self.enable_register(True)
        time.sleep(.001)
        self.enable_register(False)

    def convert_number_to_buffer(self,number):

        #Check if the input number exceeds buffer size
        if len(bin(number)) > self.size + 2:
            #Raise ValueError if number exceeds buffer size
            raise ValueError("Number is to big for the buffer size")
        #Convert the number into a binary string, remove unecessary prefix ("0b") and make sure the binary string is at least length = 3
        binary_string = bin(number).replace("0b","").zfill(self.size)
        #Convert binary string into boolean array
        return [binary_string[i] == "1" for i in range(self.size)]






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
