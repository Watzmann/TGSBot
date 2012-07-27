"""Welcome message as login trigger and log in mechanics."""

from operation.basics import Request, Response

class Welcome(Request):
    def __init__(self, dispatch, manage,):
        self.expected = "WELCOME TO"
        Request.__init__(self, dispatch, manage,)

    def received(self, message):
        self.purge()
        self.dispatch.login()

class Login(Request):

    class Answer(Response):

        def __init__(self, user):
            Response.__init__(self, '')
            self.complex_answer(self.login_answer, [user,])

        def login_answer(self, expected, message):
            user = expected[0]
            try:
                ret = not message[1].startswith('1 %s' % user)
                ret += not message[2].startswith('2 %s' % user)
                ret += not message[3].startswith('3')
                ret += not message[4].startswith('+--')
                m = 5
                while not message[m].startswith('+--'):
                    m += 1
                ret += not message[m+1].startswith('4')
                m = m + 3
                while message[m].startswith('5 '):
                    m += 1
                ret += not message[m].startswith('6')
            except:
                return False
            return not ret

    def __init__(self, dispatch, manage, user):
        self.expected = self.Answer(user)
        Request.__init__(self, dispatch, manage,)

    def received(self, message):
##        print 'TESTE -------------------', message
        expected_answer = self.expected.test(message)
##        print 'FINDE -------------------', expected_answer
        if expected_answer:
            self.purge()
            self.dispatch.set_boardstyle()
            self.dispatch.query_status()
        return expected_answer

    def update(self,):
        self.manage['default'] = self
