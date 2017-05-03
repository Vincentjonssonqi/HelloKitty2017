import time
from threading import Timer
from datetime import datetime,date,timedelta
import os
from .keypad import Keypad
from .buffer import Buffer
from .buzzer import Buzzer
from .led import Led

from .unlockattempt import UnlockAttempt
class Lock:

    def __init__(self,enable_side_channel,printer):
        self.locked = True
        self.enable_side_channel = enable_side_channel
        self.has_components = False
        self.has_buffer = False
        self.failed_attempts = 0
        self.printer = printer
        self.password_line_timer = None

    def init_buffer(self,buffer_pins,buffer_disable_pin,clock_pin,not_real):
        self.buffer = Buffer(buffer_pins,buffer_disable_pin,clock_pin,not_real)
        self.has_buffer = True

    def init_keypad(self,type,keys):
        if self.has_buffer:
            self.printer.replace("status","You need a buffer for the keypad, make sure you initilize it before you init the keypad")
        self.keypad = Keypad(keys,self.buffer,self.show)

    def init_components(self,buzzer_pin,success_led_pin,error_led_pin):
        if not self.has_buffer:
            self.printer.replace("status","Need to initilize buffer before you do this mate")

        self.buzzer = Buzzer(buzzer_pin,self.buffer)
        self.success_led = Led("red",success_led_pin,self.buffer)
        self.error_led = Led("green",error_led_pin,self.buffer)
        self.has_components = True

    def set_password(self,password):
        self.password = password

    def config_max_lockout(self,attempt_limit,deactivation_duration):
        self.attempt_limit = attempt_limit
        self.deactivation_duration = deactivation_duration

    def config_time_lockout(self,opens_at,closes_at):
        self.opens_at = datetime.combine(date.min,opens_at) - datetime.min
        self.closes_at = datetime.combine(date.min,closes_at) - datetime.min

    #init_event_loop--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        #Description
        #Initilizes the loop that listens on pins and decides what events to trigger


    def start(self):
        self.log("{},{},{}".format(datetime.now().isoformat(),0,"Start"))
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

            if self.password_line_timer:
                self.password_line_timer.cancel()
            self.update_password_line(attempt.password,False)
            self.password_line_timer = Timer(1.0,self.update_password_line,(attempt.password,True))
            self.password_line_timer.start()
            #This solution only only
            #if self.is_password_complete(attempt.password):
            #    self.unlock(attempt)
            #    attempt = None

            #Side channel attack solution




    def update_password_line(self,password,cover_all):
        stars = (len(password) - 0 if cover_all else 1 )*"*"
        key = password[len(password)-1] if not cover_all else ""
        dashes = (len(self.password) - len(password))*"-"
        self.printer.replace("keypad","[ {0}{1}{2} ]".format(stars,key,dashes))

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
        if not self.has_components:
            self.printer.replace("status","There are no initilized components so I cannot show any state live")
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
        self.update_password_line("",False)
        while countdown >= 0:
            progress = int(40*(1-(float(countdown)/float(duration))))
            self.printer.replace("status","Keypad deactivated: [{0}{1}] {2}s remaining".format((40- progress)*"=",progress*" ",countdown))
            time.sleep(1)
            countdown -= 1
        self.printer.replace("status","Activated keypad")

    def lock(self):
        self.printer.replace("status","Wait for user input...")
        self.failed_attempts = 0
        self.locked = True
        self.show("lock")
        self.printer.replace("lock status","LOCKED")

    def unlock(self,attempt):
        if self.is_password_complete_and_correct(attempt.password):
            self.printer.replace("status","Password was correct!")
            attempt.outcome(True)
            self.locked = False
            self.printer.replace("lock status","UNLOCKED")
            self.show("unlocked")
            self.deactivate(3)
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
