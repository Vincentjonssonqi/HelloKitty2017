#!/usr/bin/python
import signal
import sys
from classes.lock import Lock

#CONSTANTS--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

BUFFER_PINS = [11,10,9]
BUZZER_PIN = 7
RED_LED_PIN = 6
GREEN_LED_PIN = 5
KEYPAD_KEYS = [["1","2","3"],["4","5","6"],["7","8","9"],["*","0","#"]]
ATTEMPT_LIMIT = 3
DEACTIVATION_DURATION = 60                                                                      #The number of seconds the lock will be deactivated for if an attempt limit is reached
AVAILABLE_AT =  

#GLOBAL VARIABLES------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





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
        lock.quit()
        sys.exit(0)


#init--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description
    #Initilizes variables and starts the event loop


def init():

    lock = Lock(get_password(),ATTEMPT_LIMIT,DEACTIVATION_DURATION,KEYPAD_KEYS,BUFFER_PINS,BUZZER_PIN,GREEN_LED_PIN,RED_LED_PIN)

    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()






init()
