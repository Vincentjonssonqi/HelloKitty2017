import datetime
class UnlockAttempt:
    def __init__(self):
        self.started_at = datetime.datetime.now()
        self.finished_at = None
        self.password = ""
        self.was_successful = False

    def __str__(self):
        return "{},{},{}".format(self.finished_at.isoformat(),1 if self.was_successful else -1,self.password)
    def __repr__(self):
        return self.__str__()

    def outcome(self,was_successful):
        self.was_successful = was_successful
        self.finished_at = datetime.datetime.now()
