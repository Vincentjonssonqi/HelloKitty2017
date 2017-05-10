from .component import Component
class Buzzer(Component):
    def __init__(self,command,buffer):
        self.command = command
        self.buffer = buffer
