from .component import Component
class Interupt(Component):
    def __init__(self,command,buffer):
        self.command = command
        self.buffer = buffer
        
    def clock(self):
        if self.is_on:
           self.buffer.write(self.buffer.neutral_command)
        else:
            self.buffer.write(self.command)
            

