"""Welcome message as login trigger and log in mechanics."""

from twisted.python import log
from operation.basics import Request, Response

TRACE = 15
VERBOSE = 17

import logging
logging.addLevelName(TRACE, 'TRACE')
logging.addLevelName(VERBOSE, 'VERBOSE')
print 'welcome could set logginglevel'

class Welcome(Request):
    def __init__(self, dispatch, manage,):
        self.expected = "WELCOME TO"
        Request.__init__(self, dispatch, manage,)

    def received(self, message):
        log.msg('WELCOME tests: %s' % message[0], logLevel=VERBOSE)
        log.msg('WELCOME applies '+'+'*40, logLevel=VERBOSE)
        self.purge()
        self.dispatch.login()
        del message[0:len(message)]
        return True

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
        if len(message) < 2:
            first_line = message[0]
        else:
            first_line = message[1]
        log.msg('LOGIN tests: %s' % first_line, logLevel=VERBOSE)
        expected_answer = self.expected.test(message)
        if expected_answer:
            log.msg('LOGIN applies '+'+'*40, logLevel=VERBOSE)
            self.purge()
            del message[0:len(message)]
            self.dispatch.set_boardstyle()
            self.dispatch.query_status()
        else:
            log.msg('LOGIN applies NOT '+'-'*36, logLevel=VERBOSE)
        return expected_answer

    def update(self,):
        self.manage['default'] = self
