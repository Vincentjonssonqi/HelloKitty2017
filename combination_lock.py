import signal
import time
import sys
import datetime
from classes.lock import Lock
from classes.printer import Printer
import RPi.GPIO as GPIO
#CONSTANTS--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

BUFFER_PINS = [11,10,9]
BUFFER_DISABLE_PIN = 15
BUFFER_CLOCK_PIN = 14

BUFFER_NEUTRAL_COMMAND = 0
BUZZER_COMMAND = 4
RED_LED_COMMAND = 6
GREEN_LED_COMMAND = 5
INTERUPT_COMMAND = 7

ATTEMPT_LIMIT = 3
#The number of seconds the lock will be deactivated for if an attempt limit is reached
DEACTIVATION_DURATION = 5
#Opens at 9AM
OPENS_AT = datetime.time(9,0)
 #Closes at 21PM
CLOSES_AT = datetime.time(9,0)


ALLOW_MAX_LOCKOUT = True
#If you wish to try the code without the actual keypad you make this True, and random keys will be entered at random time intervals
NO_REAL_BUFFER = True
#This value is used to configure the lock to be vulnerable to a side channel attack
ENABLE_SIDE_CHANNEL_ATTACK = False
#Can be either polling or interupt
KEYPAD_TYPE = "interupt"
KEYPAD_KEYS = [["1","2","3"],["4","5","6"],["7","8","9"],["*","0","#"]]


#GLOBAL VARIABLES------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

lock = None
printer = Printer()
def get_password():
    pswrd = ""
    try:
        #We use a try here to avoid a crash if the file does not exists
        #Load the password.txt file into memory
        password_file = open("password.txt","r")
        #Store the content of the file into the password variable
        return password_file.read()
    except FileNotFoundError:
        #Except FileNotFoundError as the file might not exist
        #Assign initial default password
        return "1234"
        print("error")




def signal_handler(signal, frame):
    printer.replace("status","Preparing to exit")

    lock.quit()
    printer.replace("status","Done")
    time.sleep(.2)
    printer.replace("status","Good bye Mike! If you happen to be anybody else then we are in a bit of tought situation. You see this is message will always be the same. Soo.. either you change your name or you have have to remember not to read this last message on exit.")
    GPIO.cleanup()
    sys.exit(1)

def setup_print_layout():
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
#init--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description
    #Initilizes variables and starts the event loop


def init():


    setup_print_layout()
    signal.signal(signal.SIGINT, signal_handler)


    global lock
    lock = Lock(ENABLE_SIDE_CHANNEL_ATTACK,printer)

    lock.init_buffer(BUFFER_PINS,BUFFER_DISABLE_PIN,BUFFER_CLOCK_PIN,BUFFER_NEUTRAL_COMMAND,INTERUPT_COMMAND,NO_REAL_BUFFER)
    lock.init_keypad(KEYPAD_TYPE,KEYPAD_KEYS)
    lock.init_components(BUZZER_COMMAND,GREEN_LED_COMMAND,RED_LED_COMMAND)
    lock.config_time_lockout(OPENS_AT,CLOSES_AT)
    lock.config_security(ENABLE_SIDE_CHANNEL_ATTACK)
    lock.set_password(get_password())


    if ALLOW_MAX_LOCKOUT:
        lock.config_max_lockout(ATTEMPT_LIMIT,DEACTIVATION_DURATION)

    lock.start()






init()
