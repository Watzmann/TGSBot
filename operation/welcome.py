#
# (c) Copyright 2012 Andreas Hausmann
# This file is part of TGSBot.
# Permission to copy or use is limited. Please see LICENSE for information.
#
"""Welcome message as login trigger and log in mechanics."""

import time
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
        self.label = 'WELCOME'
        Request.__init__(self, dispatch, manage,)

    def received(self, message):
        log.msg(self.msg_tests % message[0], logLevel=VERBOSE)
        log.msg(self.msg_applies + '+'*40, logLevel=VERBOSE)
        self.purge()
        self.dispatch.login()
        del message[0:len(message)]
        return True

class Login(Request):

    def __init__(self, dispatch, manage, callback, expected="BOTUID "):
        self.expected = expected
        self.callback = callback
        self.label = 'LOGIN'
        Request.__init__(self, dispatch, manage,)

    def received(self, message):
        first_line = message[0]
        log.msg(self.msg_tests % first_line, logLevel=VERBOSE)
        uid = first_line.split()[1]
        self.callback(uid)
        log.msg(self.msg_applies + '+'*40, logLevel=VERBOSE)
        time_used = time.time() - self.sent_request
        log.msg(self.msg_waited % time_used, logLevel=logging.INFO)
        self.purge()
        del message[0:1]
        self.dispatch.login_hook()
        return True
