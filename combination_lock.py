
from .keypad import Keypad

#CONSTANTS--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

BUFFER_PINS = [11,10,9]
KEYPAD_KEYS = [["1","2","3"],["4","5","6"],["7","8","9"],["*","0","#"]]


#GLOBAL VARIABLES------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


keypad = new Keypad(BUFFER_PINS,KEYPAD_KEYS)
password = ""



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


#init_event_loop--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description
    #Initilizes the loop that listens on pins and decides what events to trigger


def init_event_loop():
    while True:
        key = keypad.next_key()
        print(key)




#init--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description
    #Initilizes variables and starts the event loop


def init():
    password = get_password()
    init_event_loop()







init()
