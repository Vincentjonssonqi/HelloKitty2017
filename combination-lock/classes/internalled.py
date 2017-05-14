import RPi.GPIO as GPIO
class InternalLed:
    def __init__(self,pin):
        self.pin = pin
        GPIO.setup(pin,GPIO.OUT)



    #on--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
    #Turns on the led if it is not already on
    def on(self):
        GPIO.output(self.pin,True)



    #off--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
    #Turns off the led if it is not already on
    def off(self):
        GPIO.output(self.pin,False)
