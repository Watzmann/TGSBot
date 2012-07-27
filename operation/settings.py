"""Commands about toggles, settings, etc."""

from operation.basics import Request

class Toggle(Request):
    def __init__(self, dispatch, manage,):
        self.expected = "The current settings are:"
        Request.__init__(self, dispatch, manage,)

    def receive(self, message):
        lines = message.splitlines()
        self.toggles = {}
        try:
            for t in lines[1:]:
                s = t.split()
                self.toggles[s[0]] = s[-1]
        except:
            raise RuntimeError('Toggle got unexpected data: >%s<' % message)
        self.dispatch.toggles = self.toggles
        if self.toggles['ready'] == 'NO':
            self.set_ready()
        self.purge()

    def set_ready(self,):
        self.dispatch.send_server('toggle ready')
        self.dispatch.toggles['ready'] = 'YES'

class Join(Request):
    def __init__(self, dispatch, manage,):
        self.expected = "You start"
        #** You are now playing a 7 point match with hannes.
        #You are now playing with hannes. Your running match was loaded.
        Request.__init__(self, dispatch, manage,)

    def receive(self, message):
##        print 'TESTE -------------------', message
        expected_answer = self.expected.test(message)
##        print 'FINDE -------------------', expected_answer
        if expected_answer:
            self.purge()
        return expected_answer
