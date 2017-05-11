
from .lockpick import Lockpick
TYPE = "interrupt"
LENGTH = 4
ATTEMPT_TIMEOUT = 3.5
AUTOMATIC_TIMING_ANALYSIS = True
lockpick = Lockpick(TYPE,LENGTH,ATTEMPT_TIMEOUT,AUTOMATIC_TIMING_ANALYSIS)
print("And the password is, drumrolllll.... {}".format(lockpick.get_password())
