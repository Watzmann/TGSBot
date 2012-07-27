"""Welcome message as login trigger and log in mechanics."""

from operation.basics import Request, Answer

class Welcome(Request):
    def __init__(self, dispatch, manage,):
        self.expected = "WELCOME TO"
        Request.__init__(self, dispatch, manage,)

    def receive(self, message):
        self.purge()
        self.dispatch.login()

class Login(Request):
    def __init__(self, dispatch, manage, user):
        self.expected = Answer('').complex_answer('login', [user,])
        Request.__init__(self, dispatch, manage,)

    def receive(self, message):
##        print 'TESTE -------------------', message
        expected_answer = self.expected.test(message)
##        print 'FINDE -------------------', expected_answer
        if expected_answer:
            self.purge()
            self.dispatch.query_status()
        return expected_answer

    def update(self,):
        self.manage['default'] = self
