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
        self.expected = "login: "
        Request.__init__(self, dispatch, manage,)

    def received(self, message):
        log.msg('WELCOME tests: %s' % message[0], logLevel=VERBOSE)
        log.msg('WELCOME applies '+'+'*40, logLevel=VERBOSE)
        self.purge()
        self.dispatch.login()
        del message[0:len(message)]
        return True

class Login(Request):

    def __init__(self, dispatch, manage, callback, expected="BOTUID "):
        self.expected = expected
        self.callback = callback
        Request.__init__(self, dispatch, manage,)

    def received(self, message):
        first_line = message[0]
        log.msg('LOGIN tests: %s' % first_line, logLevel=VERBOSE)
        uid = first_line.split()[1]
        self.callback(uid)
        log.msg('LOGIN applies '+'+'*40, logLevel=VERBOSE)
        self.purge()
        del message[0:1]
        self.dispatch.login_hook()
        return True
