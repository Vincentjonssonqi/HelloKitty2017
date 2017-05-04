import time
class Keypad:
    def __init__(self,keys,keypad_type,buffer,cb):
        self.keys = keys
        self.use_interupt = keypad_type == "interupt"
        self.event_cb = cb
        self.buffer = buffer





    #next_key--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
    #Checks if a key is pressed and returns the key when the user has released the press

    #Returns:
    #A string with the pressed key's face value.
    def on_key(self,cb):
        if self.use_interupt:
            self.start_keypad_interupt(cb)
        else:
            self.start_keypad_polling(cb)

    #start_keypad_interupt

    #Description:
    #Asks the pi to call the poll_keypad function when an active column is detected
    #The difference between this and constantly polling is that you save a lot of resources when you
    #only have to poll the keypad when a person is actually pressing a key

    def start_keypad_interupt(self,cb):
        print("stared interupt")
        #We start of by writing switching the keypad state to interupt mode
        #This basically mean that we ensure that we drive a 0 onto all rows at the same time always
        #At least until we detect a key press
        #When that happens the interupt should be triggered and we perform the same polling as before
        #The advantage of this is that we do not poll all the time, only when the user is actually
        #interacting with the keypad
        for i in len(self.pins):
            GPIO.add_event_detect(self.pins[i], GPIO.FALLING, callback=lambda pin: self.interupt_callback(pin,cb))

    def interupt_callback(self,pinId,cb):
        for i in len(self.pins):
            GPIO.remove_event_detect(self.pins[i])
        print(pinId)
        key = self.check_keypad()
        if key:
            cb(key)
            self.start_keypad_interupt(cb)
        else:
            raise ValueError("Thekey should have been detected")


    def start_keypad_polling(self,cb):
        while True:
            key = self.check_keypad()
            if key:
                cb(key)
    #poll_keypad----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
    #Goes through all rows and checks if a key is pressed

    #Returns:
    #None or the key value (String)


    def check_keypad(self):
        for row in range(4):
            key = self.poll_row(row)

            if key:
                return key
        return None





    #poll_row----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
    #Polls the row and if an active column is present, return the key value, ones the key has been released


    def poll_row(self,row):
        #print(row)
        self.buffer.write(row)
        time.sleep(20)
        column = self.buffer.read()
        if column != None:
            self.event_cb("key_down")
            return self.poll_key(row,column)
        return None;



    #poll_key----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
    #Polls a single row and checks a single column until the button is released


    def poll_key(self,row,column):
        next_column = column
        while next_column != None and next_column == column:
            self.buffer.write(row)
            next_column = self.buffer.read()
        self.event_cb("key_up")
        #print("column {}, row {}".format(column,row))
        #print(self.keys[row][column])
        return self.keys[row][column]
