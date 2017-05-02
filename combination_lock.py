import signal
import time
import sys
import datetime
from classes.lock import Lock
from classes.printer import Printer

#CONSTANTS--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

BUFFER_PINS = [11,10,9]
BUZZER_PIN = 7
RED_LED_PIN = 6
GREEN_LED_PIN = 5
KEYPAD_KEYS = [["1","2","3"],["4","5","6"],["7","8","9"],["*","0","#"]]
ATTEMPT_LIMIT = 10
DEACTIVATION_DURATION = 5                                                                      #The number of seconds the lock will be deactivated for if an attempt limit is reached
OPENS_AT = datetime.time(9,0)                                                                   #Opens at 9AM
CLOSES_AT = datetime.time(9,0)                                                             #Closes at 17PM
NO_HARDWARE = True

#GLOBAL VARIABLES------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


lock = None
printer = Printer()

#get_password------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
    #Loads password combination string from password.txt
    #or set password variable to the default pass to "1234"


def get_password():
    pswrd = ""
    try:                                                                                        #We use a try here to avoid a crash if the file does not exists
        password_file = open("password.txt","r")                                                #Load the password.txt file into memory
        pswrd = password_file.read()                                                            #Store the content of the file into the password variable
    except FileNotFoundError:                                                                   #Except FileNotFoundError as the file might not exist
        pswrd = "1234"                                                                          #Assign initial default password
        print("error")
    finally:
        return pswrd
        print(pswrd)




def signal_handler(signal, frame):
    printer.replace("status","Preparing to exit")
    
    lock.quit()
    printer.replace("status","Done")
    time.sleep(.2)
    printer.replace("status","Good bye Mike! If you happen to be anybody else then we are in a bit of tought situation. You see this is message will always be the same. Soo.. either you change your name or you have have to remember not to read this last message on exit.")
    sys.exit(1)

def setup_print_layout():
    printer.add("title","PROGRAM: COMBINATION LOCK")
    printer.add("subtitle","DESCRIPTION: Enter code on keypad")
    printer.add("password","PASSWORD: []")
    printer.add("status","STATUS: Initilizing..")
#init--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description
    #Initilizes variables and starts the event loop


def init():
    
    signal.signal(signal.SIGINT, signal_handler)
    setup_print_layout()
    #printer.replace("status","STATUS: test.")
    #time.sleep(2)
    #printer.replace("title","Title2.")
    #time.sleep(2)
    #printer.replace("password","password.")
    global lock
    lock = Lock(printer,get_password(),ATTEMPT_LIMIT,DEACTIVATION_DURATION,OPENS_AT,CLOSES_AT,KEYPAD_KEYS,BUFFER_PINS,BUZZER_PIN,GREEN_LED_PIN,RED_LED_PIN,NO_HARDWARE)
    lock.boot()






init()
