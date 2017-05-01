#!/usr/bin/python
import time
import datetime
import os
from classes.keypad import Keypad
from classes.buffer import Buffer
from classes.buzzer import Buzzer
from classes.led import Led
from classes.unlockattempt import UnlockAttempt
class Lock:

    failed_attempts = 0
    def __init__(self,password,attempt_limit,deactivation_duration,keypad_keys,buffer_pins,buzzer_pin,success_led_pin, error_led_pin):
        print("inside lock constructor")
        self.locked = True
        self.password = password
        self.attempt_limit = attempt_limit
        self.deactivation_duration = deactivation_duration
        self.buffer = Buffer(buffer_pins,True)
        self.keypad = Keypad(keypad_keys,buffer)

        self.buzzer = Buzzer(buzzer_pin,buffer)

        self.success_led = Led("red",success_led_pin,buffer)
        self.error_led = Led("green",error_led_pin,buffer)

        self.log("{},{}".format(datetime.datetime.now().isoformat(),0))

        self.init_event_loop()


    #init_event_loop--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        #Description
        #Initilizes the loop that listens on pins and decides what events to trigger


    def init_event_loop():
        attempt = None
        while True:
            key = self.keypad.next_key()
            print(key)
            if not attempt:
                attempt = UnlockAttempt()

            attempt.password += key
            attempt = attempt if evaluate_unlock_attempt(attempt) else None


    #evaluate_unlock_attempt-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    def evaluate_unlock_attempt(attempt):
        correct_content = self.password.startswith(attempt.password)
        correct_length = len(self.password) == len(attempt.password)

        if not correct_content:
            self.unlock_attempt_failed(attempt)
            return False
        else:
            if correct_length:
                self.unlock_attempt_successeded(attempt)
                return False
        return True






    #unlock_attempt_failed-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        #Write attempt

    def unlock_attempt_failed(attempt):
        self.buzzer.on()
        self.error_led.on()
        attempt.outcome(False)

        self.log_attempt(str(attempt))
        self.sleep(.5)
        self.buzzer.off()
        self.error_led.off()


        self.failed_attempts += 1
        if self.failed_attempts >= self.attempt_limit:
            self.deactivate()
            self.failed_attempts = 0



    #unlock_attempt_successeded-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        #Description:
        #
    def unlock_attempt_successeded(attempt):
        self.buzzer.on()
        self.success_led.on()
        self.locked = False

        attempt.outcome(True)

        self.log(str(attempt))
        self.sleep(5)

        self.buzzer.off()
        self.success_led.off()
        self.locked = True
        self.failed_attempts = 0


    def deactive():
        countdown = self.deactivation_duration
        while countdown > 0:
            print("LOCKED {}s remaining".format(countdown))
            time.sleep(1)
            countdown -= 1



    def log(line):
        need_titles = not os.path.isfile('unlock-attempt.logs.csv')
        attempt_log_file = open("logs.csv","a")
        if need_titles:
            attempt_log_file.write("#","Success\n")
        attempt_log_file.write("{}\n".format(line))
        attempt_log_file.close()


    def quit():
        self.generate_summery_graph()
        self.log("{},{}".format(datetime.datetime.now().isoformat(),0))
