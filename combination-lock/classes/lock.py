import time
from threading import Timer
from datetime import datetime,date,timedelta
import os
from .keypad import Keypad
from .buffer import Buffer
from .buzzer import Buzzer
from .internalled import InternalLed
from .led import Led
import os
import subprocess

from .unlockattempt import UnlockAttempt
class Lock:

    def __init__(self,enable_side_channel,printer):
        self.locked = True
        self.enable_side_channel = enable_side_channel
        self.has_components = False
        self.has_buffer = False
        self.has_attempt_timeout = False
        self.is_vulnerable = False
        self.failed_attempts = 0
        self.printer = printer
        self.password_line_timer = None
        self.key_pressed = False
        self.timeout_timer = None
        self.printer.replace("status","LOCKED")
        self.printer.replace("logs","Created Lock")

    def init_buffer(self,buffer_pins,buffer_control_pin,register_control_pin,column_change_pin,neutral_command,interupt_command,not_real):
        self.buffer = Buffer(buffer_pins,buffer_control_pin,register_control_pin,column_change_pin,neutral_command,interupt_command,not_real)
        self.has_buffer = True
        self.printer.replace("logs","Buffer initilized")

    def init_keypad(self,keypad_type,keys):
        if self.has_buffer:
            self.printer.replace("logs","You need a buffer for the keypad, make sure you initilize it before you init the keypad")
        self.keypad = Keypad(keys,keypad_type,self.buffer,self.keypad_callback)
        self.printer.replace("logs","Keypad initilized")

    def init_components(self,buzzer_command,success_led_command,error_led_command):
        if not self.has_buffer:
            self.printer.replace("logs","Need to initilize buffer before you do this mate")
        self.buzzer = Buzzer(buzzer_command,self.buffer)
        self.success_led = Led("green",success_led_command,self.buffer)
        self.error_led = Led("red",error_led_command,self.buffer)


        self.has_components = True
        self.printer.replace("logs","Components initilized")

    def set_password(self,password):
        self.password = password
        self.printer.replace("logs","Password has been set")

    def config_max_lockout(self,attempt_limit,deactivation_duration):
        self.attempt_limit = attempt_limit
        self.deactivation_duration = deactivation_duration
        self.printer.replace("logs","Max lockout configured")

    def config_attempt_timeout(self,duration,timeout_led_pins):
        self.timeout_leds = map(lambda pin: InternalLed(pin), timeout_led_pins)
        self.attempt_timeout_duration = duration
        self.has_attempt_timeout = True

    def config_time_lockout(self,opens_at,closes_at):
        self.opens_at = datetime.combine(date.min,opens_at) - datetime.min
        self.closes_at = datetime.combine(date.min,closes_at) - datetime.min
        self.printer.replace("logs","Time lockout configured")

    def config_security(self,is_vulnerable):
        self.is_vulnerable = is_vulnerable
        self.printer.replace("logs","Security configured")
    #init_event_loop--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        #Description
        #Initilizes the loop that listens on pins and decides what events to trigger


    def start(self):
        self.log("{},{},{}".format(datetime.now().isoformat(),0,"Start"))
        self.attempt = None
        while True:
            if not self.key_pressed:
                self.keypad.next_key()
        self.printer.replace("logs","Lock is live and waiting for user input!")

    def keypad_callback(self,event,key):
        if event == "key_down":
            self.show("key_down")
            self.on_key(key)
            self.key_pressed = True
        elif event == "key_up":
            self.key_pressed = False
            self.show("")

    def on_key(self,key):

        seconds_to_open = self.is_open()
        if seconds_to_open > 0:
            self.deactivate(seconds_to_open)
            return
        if not self.attempt:
            self.attempt = UnlockAttempt()
            self.printer.replace("logs","Attempt {0}".format(self.failed_attempts + 1))


        self.attempt.password += key
        self.printer.replace("logs","Attempted password {0}".format(self.attempt.password))

        self.start_password_timer()

        if self.has_attempt_timeout:
            self.reset_attempt_timeout()
            self.start_attempt_timeout()
        #Tries to unlock the safe on every key entery when is_vulnerable is set to True
        #This functionality exists so that we candemmonstrate the side channel attack
        #If is_vulnerable is set to False, the lock will only evaluate the code
        #once the attempted password is the same size as the actual password
        if self.is_vulnerable or self.is_password_complete(self.attempt.password):
            self.cancel_password_timer()
            self.unlock()


    def start_password_timer(self):
        if self.password_line_timer:
            self.password_line_timer.cancel()
        self.update_password_line(self.attempt.password,False)
        self.password_line_timer = Timer(1.0,self.update_password_line,(self.attempt.password,True))
        self.password_line_timer.start()
    def cancel_password_timer(self):
        if self.password_line_timer:
            self.password_line_timer.cancel()
            self.password_line_timer = None

    def start_attempt_timeout(self):
        self.update_attempt_timeout(0.0)
    def update_attempt_timeout(self,time):

        delta_time = float(self.attempt_timeout_duration)/float(len(self.timeout_leds))

        new_total_time = time + delta_time
        led_index = int((new_total_time/float(self.attempt_timeout_duration)) * float(len(self.timeout_leds)))
        if (new_total_time <= float(self.attempt_timeout_duration)):
            self.timeout_leds[led_index - 1].on()
            self.timeout_timer = Timer(delta_time,self.update_attempt_timeout,(new_total_time,))
            self.timeout_timer.start()
        else:
            self.failed_to_unlock()

    def reset_attempt_timeout(self):
        if self.timeout_timer:
            self.timeout_timer.cancel()
        for i in range(len(self.timeout_leds)):
            self.timeout_leds[i].off()

    def cancel_attempt(self):
        self.attempt = None
        self.cancel_password_timer()
        self.reset_attempt_timeout()
    def update_password_line(self,password,cover_all):
        stars = (len(password) - (0 if cover_all else 1) )*"*"
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
            self.printer.replace("logs","There are no initilized components so I cannot show any state live")
        if state == "unlocked":
            self.buzzer.on()
            self.success_led.on()
        elif state == "error":
            self.buzzer.on()
            self.error_led.on()
        elif state == "key_down":

            self.buzzer.on()
        else:
            self.buzzer.off()
            #This will turn off automatically with the multi vibrator thingy :P
            #self.success_led.off()
            self.error_led.off()


    def deactivate(self,duration):
        countdown = duration
        self.update_password_line("",True)
        while countdown > 0:
            progress = int(40*(1-(float(countdown)/float(duration))))
            self.printer.replace("logs","Keypad deactivated: [{0}{1}] {2}s remaining".format((40- progress)*"=",progress*" ",countdown))
            time.sleep(.7)
            countdown -= 1
        self.printer.replace("logs","Activated keypad")

    def lock(self):
        self.locked = True
        self.show("lock")
        self.printer.replace("status","LOCKED")
        self.log("{},{},{}".format(datetime.now().isoformat(),0,"Locked"))

    def unlock(self):
        if self.is_password_complete_and_correct(self.attempt.password):
            self.succeeded_to_unlock()
            return 1
        elif self.is_password_correct(self.attempt.password):
            return 0
        else:
            self.failed_to_unlock()
            return -1




    def succeeded_to_unlock(self):
        self.printer.replace("logs","Password was correct!")
        self.attempt.outcome(True)

        self.locked = False
        self.printer.replace("status","UNLOCKED")
        self.show("unlocked")
        self.log("{},{},{}".format(datetime.now().isoformat(),0,"Locked"))
        self.log(str(self.attempt))
        self.cancel_attempt()
        self.deactivate(3)
        self.log("{},{},{}".format(datetime.now().isoformat(),1,"Unlocked"))
        self.lock()

    def failed_to_unlock(self):
        self.printer.replace("logs","Wrong password!")
        self.log("{},{},{}".format(datetime.now().isoformat(),0,"Locked"))
        self.attempt.outcome(False)

        self.show("error")

        self.log(str(self.attempt))
        self.cancel_attempt()
        self.deactivate(1)
        self.show("")
        self.failed_attempts += 1
        if self.failed_attempts >= self.attempt_limit:

            self.deactivate(self.deactivation_duration)
            self.failed_attempts = 0
        self.log("{},{},{}".format(datetime.now().isoformat(),-1,"Locked"))
        self.log("{},{},{}".format(datetime.now().isoformat(),0,"Locked"))

    def log(self,line):
        #print("Writing to log.csv: {}".format(line))
        self.printer.replace("logs","Updating access logs..")
        need_titles = not os.path.isfile('logs.csv')
        attempt_log_file = open("logs.csv","a")
        if need_titles:
            attempt_log_file.write("#,Success,Message\n")
        attempt_log_file.write("{0}\n".format(line))
        attempt_log_file.close()

    def generate_graph(self):
        p = subprocess.Popen("gnuplot chartgenerator.p", shell = True)
        os.waitpid(p.pid, 0)


    def quit(self):
        self.lock()
        last_log = "{},{},{}".format(datetime.now().isoformat(),0,"Shut down")
        #run command line program that generates graph
        self.printer.replace("logs","Generating graph of Access Times...")
        self.generate_graph()

        self.printer.replace("logs","you can find the access time graph in the program folder named: accestime.png")
        self.log(last_log)
