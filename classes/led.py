#!/usr/bin/python
class Led(Component):
    def __init__(self,color,command,buffer):
        self.color = color
        self.command = command
        self.buffer = buffer
