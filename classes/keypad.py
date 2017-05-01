#!/usr/bin/python
from .buffer import Buffer
from .led import Led
class Keypad:
    self.on_key_down = None
    self.on_key_up = None
    def __init__(self,keys,buffer):
        self.keys = keys






    #next_key--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
    #Checks if a key is pressed and returns the key when the user has released the press

    #Returns:
    #A string with the pressed key's face value.
    def next_key(self):
        while True:
            key = poll_keypad()
            if key:
                return key


    #poll_keypad----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
    #Goes through all rows and checks if a key is pressed

    #Returns:
    #None or the column id (Interger)


    def poll_keypad(self):
        for row in range(4):
            key = poll_row(row)
            if key:
                return key
        return None





    #poll_row----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
    #Polls the row and if an active column is present, return the key value, ones the key has been released


    def poll_row(self,row):
        self.buffer.write(row)
        column = self.buffer.read()
        if column:
            return poll_key(row,column)
        return None;



    #poll_key----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
    #Polls a single row and checks a single column until the button is released


    def poll_key(row,column):
        self.buzzer.on()
        while True:
            self.buffer.write(row)
            column = self.buffer.read()
            if not column:
                self.buzzer.off()
                return self.keys[row][column]
