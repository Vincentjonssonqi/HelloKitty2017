import lockpick as l
#TYPE = "polling"
#LENGTH = 4
#ATTEMPT_TIMEOUT = 3.5
#AUTOMATIC_TIMING_ANALYSIS = True
#lockpick = Lockpick(TYPE,LENGTH,ATTEMPT_TIMEOUT,AUTOMATIC_TIMING_ANALYSIS)
print("brute force method")
a = l.Lockpick(discover_timings=False)
print("And the password using brute force, drumrolllll.... {}".format(a.brute_force()))
