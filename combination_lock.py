import signal
import time
import sys
import datetime
from classes.lock import Lock
from classes.printer import Printer

#CONSTANTS--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

BUFFER_PINS = [11,10,9]
BUFFER_FLOW_CONTROL_PIN = 14
BUZZER_PIN = 7
RED_LED_PIN = 6
GREEN_LED_PIN = 5
ATTEMPT_LIMIT = 3
DEACTIVATION_DURATION = 5                                                                       #The number of seconds the lock will be deactivated for if an attempt limit is reached
OPENS_AT = datetime.time(9,0)                                                                   #Opens at 9AM
CLOSES_AT = datetime.time(9,0)                                                                  #Closes at 17PM
NO_REAL_BUFFER = True

ALLOW_MAX_LOCKOUT = True

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
    print("\n\n\n")
    printer.add("border_top","------------------------------------------------------------------------------------------------------------",False)
    printer.add("margin_top","",False)
    printer.add("app","COMBINATION LOCK",True)
    printer.add("about","Enter the unlock code on the keypad, if the code is right, then good for you :)",True)
    printer.add("border_middle","",False)
    printer.add("lock status","BOOTING...")
    printer.add("border_middle2","",False)
    printer.add("status","Initilizing..",True)
    printer.add("keypad","[ deactivated ]",True)
    printer.add("margin_bottom","",False)
    printer.add("border_bottom","------------------------------------------------------------------------------------------------------------",False)
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
    lock = Lock(printer)

    lock.init_buffer(BUFFER_PINS,BUFFER_FLOW_CONTROL_PIN,NO_REAL_BUFFER)

    if ALLOW_MAX_LOCKOUT:
        lock.config_max_lockout(ATTEMPT_LIMIT,DEACTIVATION_DURATION)

    lock.config_time_lockout(OPENS_AT,CLOSES_AT)

    lock.set_password(get_password())

    lock.init_components(BUZZER_PIN,GREEN_LED_PIN,RED_LED_PIN)

    lock.start()






init()
