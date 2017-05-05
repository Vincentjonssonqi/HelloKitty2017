import time
class Keypad:
    def __init__(self,keys,keypad_type,buffer,cb):
        self.keys = keys
        self.use_interupt = keypad_type == "interupt"
        self.event_cb = cb
        self.buffer = buffer





    #on_key--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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
    #Use interupt approach to listen for keypad changes

    def start_keypad_interupt(self,cb):
         self.buffer.start_interupts(cb = lambda pin:self.interupt_callback(pin,cb))
        

    def interupt_callback(self,pinId,cb):
        key = self.next_key()
        cb(key)
        self.start_keypad_interupt(cb)


    def start_keypad_polling(self,cb):
        key = self.next_key()
        cb(key)
        self.start_keypad_polling(cb)
        
    def next_key(self):
        key = None
        while not key:
            key = self.check_keypad()
        return key
        
                
                
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
