import time
class Keypad:
    def __init__(self,keys,keypad_type,buffer,cb):
        self.keys = keys
        self.keypad_type = keypad_type or "polling"
        self.event_cb = cb
        self.buffer = buffer





    #next_key--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
    #Checks if a key is pressed and returns the key when the user has released the press

    #Returns:
    #A string with the pressed key's face value.
    def next_key(self):
        while True:
            key = self.poll_keypad()
            if key:
                return key

    #start_keypad_interupt

    #Description:
    #Asks the pi to call the poll_keypad function when an active column is detected
    #The difference between this and constantly polling is that you save a lot of resources when you
    #only have to poll the keypad when a person is actually pressing a key

    #returns:
    #None or the key value (String
    def start_keypad_interupt(self):
        #We start of by writing high 
    #poll_keypad----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
    #Goes through all rows and checks if a key is pressed

    #Returns:
    #None or the key value (String)


    def poll_keypad(self):
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
