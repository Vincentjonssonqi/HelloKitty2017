import lockpick as l
#TYPE = "polling"
#LENGTH = 4
#ATTEMPT_TIMEOUT = 3.5
#AUTOMATIC_TIMING_ANALYSIS = True
#lockpick = Lockpick(TYPE,LENGTH,ATTEMPT_TIMEOUT,AUTOMATIC_TIMING_ANALYSIS)

a = l.Lockpick()
print("And the password is, drumrolllll.... {}".format(a.get_password()))
