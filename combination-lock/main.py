import signal
import time
import sys
import datetime

from classes.lock import Lock
from classes.printer import Printer
from classes.buffer import Buffer

import RPi.GPIO as GPIO


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


#CONSTANTS--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


BUFFER_PINS = [11,10,9]
BUFFER_DISABLE_PIN = 15
BUFFER_CLOCK_PIN = 14
COLUMN_CHANGE_PIN = 17
TIMEOUT_LED_PINS = [5,6,12,13,16,19,20,26]
BUFFER_NEUTRAL_COMMAND = 7
BUZZER_COMMAND = 6
RED_LED_COMMAND = 5
GREEN_LED_COMMAND = 4
INTERUPT_COMMAND = 7

ATTEMPT_LIMIT = 2
#The number of seconds the lock will be deactivated for if an attempt limit is reached
DEACTIVATION_DURATION = 10
ATTEMPT_TIMEOUT_DURATION = 3
#Opens at 9AM
OPENS_AT = datetime.time(8,0)
 #Closes at 21PM
CLOSES_AT = datetime.time(8,0)


ALLOW_MAX_LOCKOUT = False
#If you wish to try the code without the actual keypad you make this True, and random keys will be entered at random time intervals
NO_REAL_BUFFER = False
#This value is used to configure the lock to be vulnerable to a side channel attack
ENABLE_SIDE_CHANNEL_ATTACK = False
#Can be either polling or interupt
KEYPAD_TYPE = "polling"
KEYPAD_KEYS = [["1","2","3"],["4","5","6"],["7","8","9"],["*","0","#"]]







#init--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description
    #Initilizes variables and starts the event loop


def init():




    #Initilize the printer and create the GUI
    printer = Printer()
    print("\n\n\n")
    printer.add("border_top","------------------------------------------------------------------------------------------------------------",False)
    printer.add("margin_top","",False)
    printer.add("app","COMBINATION LOCK",True)
    printer.add("about","Enter the unlock code on the keypad, if the code is right, then good for you :)",True)
    printer.add("border_middle","",False)
    printer.add("status","BOOTING...",True)
    printer.add("border_middle2","",False)
    printer.add("logs","Initilizing..",True)
    printer.add("keypad","[ deactivated ]",True)
    printer.add("margin_bottom","",False)
    printer.add("border_bottom","------------------------------------------------------------------------------------------------------------",False)






    #Initlize the password variable
    lock_password = ""
    #Try to read the password file
    try:
        #We use a try here to avoid a crash if the file does not exists
        #Load the password.txt file into memory
        password_file = open("password.txt","r")
        #Store the content of the file into the password variable
        lock_password = password_file.read()
    except FileNotFoundError:
        #Except FileNotFoundError as the file might not exist
        #Assign initial default password
        lock_password = "1234"






    #Create the lock buffer
    #This buffer will be used to send and recieve signals from the keypad as well as sending signals to the buzzer and leds.
    lock_buffer = Buffer(BUFFER_PINS,BUFFER_DISABLE_PIN,BUFFER_CLOCK_PIN,COLUMN_CHANGE_PIN,BUFFER_NEUTRAL_COMMAND,INTERUPT_COMMAND,NO_REAL_BUFFER)






    #Initlize the lock
    #This will create an instance of the Lock class
    global lock
    lock = Lock(lock_password,ENABLE_SIDE_CHANNEL_ATTACK,printer,lock_buffer)






    #Init the lock components (keypad, leds and buzzer)
    lock.init_keypad(KEYPAD_TYPE,KEYPAD_KEYS)
    lock.init_components(BUZZER_COMMAND,GREEN_LED_COMMAND,RED_LED_COMMAND)


    #Configure security, timeout, open hours and lockout settings.
    lock.config_attempt_timeout(ATTEMPT_TIMEOUT_DURATION,TIMEOUT_LED_PINS)
    lock.config_time_lockout(OPENS_AT,CLOSES_AT)
    lock.config_security(ENABLE_SIDE_CHANNEL_ATTACK)

    if ALLOW_MAX_LOCKOUT:
        lock.config_max_lockout(ATTEMPT_LIMIT,DEACTIVATION_DURATION)







    try:
        #This will start the lock
        lock.start()
    except KeyboardInterrupt:
        #On keyboard interrupt the we need to cleanup GPIO ports, generate chart and print good bye mike message
        lock.quit()
        printer.replace("status","Done")
        time.sleep(.2)
        print ("\n\n\n\nGood bye Mike! If you happen to be anybody else then we are in a bit of tought situation. You see this is message will always be the same. Soo.. either you change your name or you have have to remember not to read this last message on exit.")
        GPIO.cleanup()
        sys.exit(1)



init()
