"""Welcome message as login trigger and log in mechanics."""

from operation.basics import Request, Response

class Welcome(Request):
    def __init__(self, dispatch, manage,):
        self.expected = "WELCOME TO"
        Request.__init__(self, dispatch, manage,)

    def receive(self, message):
        self.purge()
        self.dispatch.login()

class Login(Request):

    class Answer(Response):

        def __init__(self, user):
            Response.__init__(self, '')
            self.complex_answer(self.login_answer, [user,])

        def login_answer(self, expected, message):
            user = expected[0]
            msgs = message.split('\n')
            try:
                ret = not msgs[1].startswith('1 %s' % user)
                ret += not msgs[2].startswith('2 %s' % user)
                ret += not msgs[3].startswith('3')
                ret += not msgs[4].startswith('+--')
                m = 5
                while not msgs[m].startswith('+--'):
                    m += 1
                ret += not msgs[m+1].startswith('4')
                m = m + 3
                while msgs[m].startswith('5 '):
                    m += 1
                ret += not msgs[m].startswith('6')
            except:
                return False
            return not ret

    def __init__(self, dispatch, manage, user):
        self.expected = self.Answer(user)
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
