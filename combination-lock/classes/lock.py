import time
import os
import subprocess
import RPi.GPIO as GPIO

from threading import Timer
from datetime import datetime,date,timedelta

from .keypad import Keypad
from .buzzer import Buzzer
from .internalled import InternalLed
from .led import Led
from .unlockattempt import UnlockAttempt


class Lock:

    def __init__(self,password,enable_side_channel,printer,lbuffer):
        self.password = password
        self.buffer = lbuffer
        self.locked = True
        self.enable_side_channel = enable_side_channel
        self.has_components = False
        self.has_attempt_timeout = False
        self.is_vulnerable = False
        self.failed_attempts = 0
        self.printer = printer
        self.password_line_timer = None
        self.key_pressed = False
        self.timeout_timer = None
        self.attempt_limit = None
        self.using_interrupt = False
        self.printer.replace("status","LOCKED")
        self.printer.replace("logs","Created Lock")
        self.busy = False






    #init_keypad-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #Creates the keypad using the internal buffer

    #Parameters:
        #keypad_type:string ("interrupt" or "polling")
        #keys: List<List<string>>

    def init_keypad(self,keypad_type,keys):
        self.using_interrupt = keypad_type == "interrupt"
        self.keypad = Keypad(keys,keypad_type,self.buffer,self.keypad_callback)
        self.printer.replace("logs","Keypad initilized")





    #init_components-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #Creates leds and buzzer components. The components use the internal buffer for communication with the hardware
        #The command is the value that will be sent on the buffer to control the hardware component

    #Parameters:
        #keypad_type:string ("interrupt" or "polling")
        #keys: List<List<string>>

    def init_components(self,buzzer_command,success_led_command,error_led_command):

        self.buzzer = Buzzer(buzzer_command,self.buffer)
        self.success_led = Led("green",success_led_command,self.buffer)
        self.error_led = Led("red",error_led_command,self.buffer)
        self.has_components = True
        self.printer.replace("logs","Components initilized")







    #config_max_lockout-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #If this is called the lock will deactivate for a specified duration after n number of failed attempts

    #Parameters:
        #attempt_limit:int
        #deactivation_duration:float

    def config_max_lockout(self,attempt_limit,deactivation_duration):
        self.attempt_limit = attempt_limit
        self.deactivation_duration = deactivation_duration
        self.printer.replace("logs","Max lockout configured")







    #config_attempt_timeout-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #If this method is called, an unlock attempt will automatically timeout after a specified duration if a new key i not entered.

    #Parameters:
        #duration:float
        #timeout_led_pins:List<int>

    def config_attempt_timeout(self,duration,timeout_led_pins):
        self.timeout_leds = list(map(lambda pin: InternalLed(pin), timeout_led_pins))
        self.attempt_timeout_duration = duration
        self.has_attempt_timeout = True





    #config_time_lockout-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #If this method is called, the lock will be activate at a specified time of day
        #and deactivate at another specified time.
        #if the open and close time are the same, then the lock will always be open

    #Parameters:
        #opens_at:datetime.Time
        #closes_at:datetime.Time

    def config_time_lockout(self,opens_at,closes_at):
        self.opens_at = datetime.combine(date.min,opens_at) - datetime.min
        self.closes_at = datetime.combine(date.min,closes_at) - datetime.min
        self.printer.replace("logs","Time lockout configured")









    #config_security-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #If the lock should be vulnerable to a side channel attack then you call
        #this method and set the is_vulenerable variable to True

    #Parameters:
        #is_vulnerable: Boolean
    def config_security(self,is_vulnerable):
        self.is_vulnerable = is_vulnerable
        self.printer.replace("logs","Security configured")











    #start--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description
        #Initilizes the loop that listens on pins and decides what events to trigger


    def start(self):
        self.log("{},{},{}".format(datetime.now().isoformat(),0,"Start"))
        #Deactivate the lock if it is started when it is supposed to be locked
        seconds_to_open = self.is_open()
        if seconds_to_open > 0:
            self.deactivate(seconds_to_open)


        self.attempt = None

        self.loop()
        self.printer.replace("logs","Lock is live and waiting for user input!")










    #loop-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #restart the next_key listener everytime the key is not pressed

    def loop(self):
        while True:
            if not self.key_pressed:
                self.keypad.next_key()









    #keypad_callback-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #Is called everytime the keypad generates a new event

    #Parameters:
        #event: string
        #key: string


    def keypad_callback(self,event,key):
        if event == "key_down":
            self.show("key_down")
            self.key_pressed = True
            self.on_key(key)

        elif event == "key_up":
            self.key_pressed = False
            self.show("")






    #on_key-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #handles everything that should be done when a key is antered into the lock
        #if the lock is already handeling a key press then the method will cancel
        #If the lock should not be open then the lock will deactivate and show the user
        #how many sseconds that remain until the lock opens
        #If the lock does not have an active attempt, this method will create an attempt
        #After this the method will update the current attempt password with th enew key
        #If the lock has an attempt timeout, then it will restart that
        #Last but not least, the method evaluates if the password is correct.

    #Parameters:
        #key:string

    def on_key(self,key):


        if self.busy:
            return
        else:
            self.busy = True


        seconds_to_open = self.is_open()
        if seconds_to_open > 0:
            self.deactivate(seconds_to_open)
            return


        if not self.attempt:
            self.attempt = UnlockAttempt()
            self.printer.replace("logs","Attempt {0}".format(self.failed_attempts + 1))


        self.attempt.password += key
        self.printer.replace("logs","Attempted password {0}".format(self.attempt.password))



        if self.has_attempt_timeout:
            self.reset_attempt_timeout()
            self.start_attempt_timeout()


        #Tries to unlock the safe on every key entery when is_vulnerable is set to True
        #This functionality exists so that we candemmonstrate the side channel attack
        #If is_vulnerable is set to False, the lock will only evaluate the code
        #once the attempted password is the same size as the actual password
        if self.is_vulnerable or self.is_password_complete(self.attempt.password):
            self.unlock(self.attempt)
        self.busy = False










    #start_password_timer-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #starts a timer that will replace the entered key string with a star in one second

    def start_password_timer(self):
        if self.password_line_timer:
            self.password_line_timer.cancel()
        self.update_password_line(self.attempt.password,False)
        self.password_line_timer = Timer(1.0,self.update_password_line,(self.attempt.password,True))
        self.password_line_timer.start()










    #cancel_password_timer-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #cancels the timer that will replace the entered key string with a star in one second

    def cancel_password_timer(self):
        if self.password_line_timer:
            self.password_line_timer.cancel()
            self.password_line_timer = None








    #update_password_line-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #replaces the password line with either a completly covered password or a password where the last key is visible
        #eg. **** or ***3

    #Parameters:
        #password:string
        #cover_all:Boolean

    def update_password_line(self,password,cover_all):
        stars = (len(password) - (0 if cover_all else 1) )*"*"
        key = password[len(password)-1] if not cover_all else ""
        dashes = (len(self.password) - len(password))*"-"
        self.printer.replace("keypad","[ {0}{1}{2} ]".format(stars,key,dashes))











    #start_attempt_timeout-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #starts a timer that recursivaly will call a function that will update the progress leds
        #When the timer have reached the final timeout duration, the current unlock attempt will be cancelled

    def start_attempt_timeout(self):
        self.update_attempt_timeout(0.0)








    #update_attempt_timeout-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #restarts the attempt timeout timer or cancels the current unlock attempt
        #if the timeout duration has been reached
    #Parameters:
        #time:float

    def update_attempt_timeout(self,duration):
        if not self.attempt:
            return
        delta_time = float(self.attempt_timeout_duration)/float(len(self.timeout_leds))

        new_total_time = duration + delta_time
        led_index = int((new_total_time/float(self.attempt_timeout_duration)) * float(len(self.timeout_leds)))
        if (new_total_time <= float(self.attempt_timeout_duration)):
            self.timeout_leds[led_index - 1].on()
            self.timeout_timer = Timer(delta_time,self.update_attempt_timeout,(new_total_time,))
            self.timeout_timer.start()
        else:
            self.busy = True
            self.reset_attempt_timeout()

            self.failed_to_unlock(self.attempt)
            self.busy = False
            if self.using_interrupt:
                self.loop()









    #reset_attempt_timeout-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #restarts the attempt timeout timer or cancels the current unlock attempt
        #if the timeout duration has been reached
    #Parameters:
        #time:float

    def reset_attempt_timeout(self):
        if self.timeout_timer:
            self.timeout_timer.cancel()
        for i in range(len(self.timeout_leds)):
            self.timeout_leds[i].off()









    #is_open-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #checks if the lock is open right now or if it should be deactivated

    #Resturns: int (The number of seconds until it opens)

    def is_open(self):
        timestamp = datetime.combine(date.min,datetime.now().time()) - datetime.min
        if self.opens_at != self.closes_at:
            if timestamp < self.opens_at or timestamp > self.closes_at:
                return (self.opens_at - timestamp).total_seconds()
        return 0








    #is_password_correct-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #checks if the enetered password is correct so far

    #Parameters:
        #password:string

    #Returns:
        #Boolean

    def is_password_correct(self,password):
        return self.password.startswith(password)







    #is_password_complete-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #checks if the entered password is the correct length, meaning that
        #the password is the same length as the correct password

    #Parameters:
        #password:string

    #Returns:
        #Boolean

    def is_password_complete(self,password):
        #print(password)
        return len(self.password) == len(password) 













    #show-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #Toggles the buzzer component and or external components leds to convey different
        #messages to the user
    #Parameters:
        #state:string
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
            self.success_led.off()
            self.error_led.off()











    #deactivate-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #Sleeps for a specified duration
        #Will wake up every second and change logs line in the UI.
        #The logs line will show a progress bar during the deactivated duration

    #Parameters:
        #duration:int
    def deactivate(self,duration):
        countdown = duration
        self.update_password_line("",True)
        while countdown > 0:
            progress = int(40*(1-(float(countdown)/float(duration))))
            self.printer.replace("logs","Keypad deactivated: [{0}{1}] {2}s remaining".format((40- progress)*"=",progress*" ",countdown))
            time.sleep(.8)
            countdown -= 1
        self.printer.replace("logs","Activated keypad")












    #lock-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #Locks the lock
        #the self.lock boolean variable do not do anything but imagine that
        #this could be used by external systems to check the state of the lock

    def lock(self):
        self.locked = True
        self.show("lock")
        self.printer.replace("status","LOCKED")
        self.log("{},{},{}".format(datetime.now().isoformat(),0,"Locked"))









    #unlock-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #Tries to unlock the lock with an attempt
        #if The password is correct in content and length then the lock will perform the successful unlock  actions.
        #if the password is only correct in content, then unlock function will not do anything
        #if the password is wrong then the lock will perform the failed unlock actions
    #Parameters:
        #attempt:UnlockAttempt

    #Returns:
        #int (-1 = failed, 0 = no action, 1 = success)

    def unlock(self,attempt):
        if not attempt:
            return
        if self.is_password_correct(attempt.password) and self.is_password_complete(attempt.password):
            self.succeeded_to_unlock(attempt)
            return 1
        elif self.is_password_correct(attempt.password):
            self.start_password_timer()
            return 0
        else:
            self.failed_to_unlock(attempt)
            return -1








    #succeeded_to_unlock-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #Unlocks the lock for a specified duration create a new log entry,cancels all timers, in the logs.csv file,
        #changes the GUI and hardware to show the unlocked state. At the end of the process, the method
        # will lock the lcok again.
    #Parameters:
        #attempt:UnlockAttempt

    def succeeded_to_unlock(self,attempt):
        if not attempt:
            return
        self.printer.replace("logs","Password was correct!")
        attempt.outcome(True)
        self.failed_attempts = 0
        self.locked = False
        self.printer.replace("status","UNLOCKED")
        self.show("unlocked")
        self.log("{},{},{}".format(datetime.now().isoformat(),0,"Locked"))
        self.log(str(attempt))

        self.attempt = None
        self.cancel_password_timer()
        self.reset_attempt_timeout()

        self.deactivate(3)
        self.log("{},{},{}".format(datetime.now().isoformat(),1,"Unlocked"))
        self.lock()








    #failed_to_unlock-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #Deactivates the lock for a specified duration, in the logs.csv file,
        #changes the GUI and hardware to show the failed state.
    #Parameters:
        #attempt:UnlockAttempt

    def failed_to_unlock(self,attempt):
        if not attempt:
            return
        self.printer.replace("logs","Wrong password!")
        self.log("{},{},{}".format(datetime.now().isoformat(),0,"Locked"))
        attempt.outcome(False)

        self.show("error")

        self.log(str(attempt))

        self.attempt = None
        self.cancel_password_timer()
        self.reset_attempt_timeout()

        self.deactivate(1)
        self.show("")
        self.failed_attempts += 1
        if self.attempt_limit and self.failed_attempts >= self.attempt_limit:

            self.deactivate(self.deactivation_duration)
            self.failed_attempts = 0
        self.log("{},{},{}".format(datetime.now().isoformat(),-1,"Locked"))
        self.log("{},{},{}".format(datetime.now().isoformat(),0,"Locked"))










    #log-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #generates an entry in the log file
    #Parameters:
        #line:string

    def log(self,line):
        #print("Writing to log.csv: {}".format(line))
        self.printer.replace("logs","Updating access logs..")
        need_titles = not os.path.isfile('logs.csv')
        attempt_log_file = open("logs.csv","a")
        if need_titles:
            attempt_log_file.write("#,Success,Message\n")
        attempt_log_file.write("{0}\n".format(line))
        attempt_log_file.close()







    #generate_graph-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #generates the access time graph and saves it to the script folder as a png
    #Parameters:
        #line:string

    def generate_graph(self):
        p = subprocess.Popen("gnuplot chartgenerator.p", shell = True)
        os.waitpid(p.pid, 0)









    #quit-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Description:
        #cleans up, generate graph and generate the last log in logs.csv

    def quit(self):
        self.lock()
        last_log = "{},{},{}".format(datetime.now().isoformat(),0,"Shut down")
        #run command line program that generates graph
        self.printer.replace("logs","Generating graph of Access Times...")
        self.generate_graph()

        self.printer.replace("logs","you can find the access time graph in the program folder named: accestime.png")
        self.log(last_log)
