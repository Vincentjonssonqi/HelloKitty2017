import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(8,GPIO.OUT)
for i in range(10):
    GPIO.output(8,True)
    time.sleep(3)
    GPIO.output(8,False)
    time.sleep(3)
