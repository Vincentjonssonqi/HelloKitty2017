import time

from datetime import datetime,date,timedelta
import os
from .keypad import Keypad
from .buffer import Buffer
from .buzzer import Buzzer
from .led import Led

from .unlockattempt import UnlockAttempt
class Lock:

    
    def __init__(self,printer,password,attempt_limit,deactivation_duration,opens_at,closes_at,keypad_keys,buffer_pins,buzzer_pin,success_led_pin, error_led_pin,no_hardware):
        self.printer = printer
        self.locked = True
        self.password = password
        self.attempt_limit = attempt_limit
        self.deactivation_duration = deactivation_duration
        self.failed_attempts = 0

        self.opens_at = datetime.combine(date.min,opens_at) - datetime.min
        self.closes_at = datetime.combine(date.min,closes_at) - datetime.min
        self.buffer = Buffer(buffer_pins,no_hardware)
        self.keypad = Keypad(keypad_keys,self.buffer,self.show)
        
        self.buzzer = Buzzer(buzzer_pin,self.buffer)

        self.success_led = Led("red",success_led_pin,self.buffer)
        self.error_led = Led("green",error_led_pin,self.buffer)

        self.log("{},{},{}".format(datetime.now().isoformat(),0,"Start"))


    #init_event_loop--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        #Description
        #Initilizes the loop that listens on pins and decides what events to trigger


    def boot(self):
        attempt = None
        while True:
            seconds_to_open = self.is_open()
            if seconds_to_open > 0:    
                self.deactivate(seconds_to_open)
            
            key = self.keypad.next_key()
            if not attempt:
                attempt = UnlockAttempt()
                self.printer.replace("status","Attempt {0}".format(self.failed_attempts + 1))

            attempt.password += key
            
            stars = (len(attempt.password) - 1 )*"*"
            key = attempt.password[len(attempt.password)-1]
            dashes = (len(self.password) - len(attempt.password))*"-"
            self.printer.replace("keypad","[ {0}{1}{2} ]".format(stars,key,dashes))
            
            if self.is_password_complete(attempt.password):
                self.unlock(attempt)
                attempt = None
            
        

    #is_open
    def is_open(self):
        timestamp = datetime.combine(date.min,datetime.now().time()) - datetime.min
        if self.opens_at != self.closes_at:
            if timestamp < self.opens_at or timestamp > self.closes_at:
                return ((self.opens_at - timestamp) + timedelta(1,0)).total_seconds()
        return 0


    #evaluate_unlock_attempt-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    def is_password_correct(self,password):
        return self.password.startswith(password)

    def is_password_complete(self,password):
        return len(self.password) == len(password)

    def is_password_complete_and_correct(self,password):
        return self.is_password_correct(password) and self.is_password_complete(password)





       

        
            



    #inidicate_unlock_success-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        #Description:
        #
    def show(self,state):
        #print(state)
        if state == "unlocked":
            self.buzzer.on()
            self.success_led.on()
        elif state == "error":
            self.buzzer.on()
            self.error_led.on()
        elif state == "key_down":
            self.buzzer.on()
            self.error_led.on()
        else:
            self.buzzer.off()
            self.success_led.off()
            self.error_led.off()


    def deactivate(self,duration):
        countdown = duration
        self.printer.replace("keypad","[ deactivated ]")
        while countdown >= 0:
            progress = int(50*(1-(float(countdown)/float(duration))))
            self.printer.replace("status","Keypad deactivated: [{0}{1}] {2}s remaining".format((50- progress)*"=",progress*" ",countdown))
            time.sleep(1)
            countdown -= 1
        self.printer.replace("status","Keypad activated")
        self.printer.replace("keypad","[ {} ]".format(len(self.password)*"-"))

    def lock(self):
        self.printer.replace("status","Locking...")
        self.failed_attempts = 0
        self.locked = True
        self.show("lock")
        self.printer.replace("status","Done!")
    
    def unlock(self,attempt):
        if self.is_password_complete_and_correct(attempt.password):
            attempt.outcome(True)        
            self.locked = False
            self.printer.replace("status","Unlocking...")
            self.show("unlocked")
            self.printer.replace("status","Done!")
            self.deactivate(5)
            self.lock()
        else:
            self.printer.replace("status","Wrong password!")
            
            attempt.outcome(False)
            self.failed_attempts += 1
            if self.failed_attempts >= self.attempt_limit:
                self.deactivate(self.deactivation_duration)
                self.failed_attempts = 0
            self.show("error")
            self.deactivate(10)
            self.show("")
        self.log(str(attempt))

        
        
    
            

    def log(self,line):
        #print("Writing to log.csv: {}".format(line))
        self.printer.replace("status","Updating logs..")
        need_titles = not os.path.isfile('logs.csv')
        attempt_log_file = open("logs.csv","a")
        if need_titles:
            attempt_log_file.write("#,Success,Message\n")
        attempt_log_file.write("{0}\n".format(line))
        attempt_log_file.close()


    def quit(self):
        lock.lock()
        #run command line program that generates graph
        self.printer.replace("status","Generating graph of Access Times...")
        last_log = "{},{},{}".format(datetime.now().isoformat(),0,"Shut down")
        self.printer.replace("status","Saving when the lock was shut down...")
        self.log(last_log)
