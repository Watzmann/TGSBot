"""Commands about toggles, settings, etc."""

from operation.basics import Request

class Join(Request):
    def __init__(self, dispatch, manage,):
        self.expected = "You start"
        #** You are now playing a 7 point match with hannes.
        #You are now playing with hannes. Your running match was loaded.
        Request.__init__(self, dispatch, manage,)

    def received(self, message):
##        print 'TESTE -------------------', message
        expected_answer = self.expected.test(message)
##        print 'FINDE -------------------', expected_answer
        if expected_answer:
            self.purge()
        return expected_answer
