from .buffer import Buffer
class Keypad:
    __init__(self,pins,keys):
        self.buffer = new Buffer(pins or [9,10,11])
        self.keys = keys or [
                ["1","2","3"],
                ["4","5","6"],
                ["7","8","9"],
                ["*","0","#"]
            ]




    #next_key--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
    #Checks if a key is pressed and returns the key when the user has released the press

    #Returns:
    #A string with the pressed key's face value.
    next_key(self):
        active_column = -1
        while True:                                                                             #This loop only exits after a key has been pressed and released
            for row in range(4):                                                                #Loop over all rows being used and check if they have a column being pressed
                key_pressed = False
                key_released = False
                column = None
                while not key_released:
                    self.buffer.write(row)                                                      #Write the row number you want to check
                    column = self.buffer.read()                                                 #Read the active column value, should return a number (1,2 or 3)
                    if column:                                                                  #Check if there is an active column
                        key_pressed = True                                                      #flag that a key have been pressed
                    else
                        if key_pressed:                                                         #check if a key_pressed flag hae been raised
                            key_released = True                                                 #if this is the case flag key_released so that the while loop while exit
                return self.keys[row][column]                                                   #Assuming row and column both start at index 0, we fetch the value from the 2d keys list and return.
