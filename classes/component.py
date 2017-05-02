class Component:
    is_on = False
    def __init__(self,command,buffer):
        self.command = command
        self.buffer = buffer

    #on--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
    #Turns on the component if it is not already on

    def on(self):
        if self.is_on is not True:
            self.buffer.write(self.command)
            self.is_on = True
    #off--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
    #Turns off the component if it is not already off

    def off(self):
        if self.is_on is True:
            self.buffer.write(self.command)
            self.is_on = False

    #toggle--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
    #Depending on the current state this function either turns the component on or off.

    def toggle(self):
        self.buffer.write(self.command)
        self.is_on = not self.is_on
