import RPi.GPIO as GPIO
class InternalLed:
    def __init__(self,pin):
        self.pin = pin
        GPIO.setup(pin,GPIO.OUT)
    def on(self):
        GPIO.output(self.pin,True)
    def off(self):
        GPIO.output(self.pin,False)
