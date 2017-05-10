import time
import sys
class Keypad:
    def __init__(self,keys,keypad_type,buffer,cb):
        self.keys = keys
        self.use_interrupt = keypad_type == "interrupt"
        self.event_cb = cb
        self.buffer = buffer


    def next_key(self):
        if self.use_interrupt:
            self.buffer.next_column_change()
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
            self.event_cb("key_down",self.keys[row][column])
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
        self.event_cb("key_up",self.keys[row][column])
        #print("column {}, row {}".format(column,row))
        #print(self.keys[row][column])
        return self.keys[row][column]
