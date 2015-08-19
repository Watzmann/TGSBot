#
# (c) Copyright 2012 Andreas Hausmann
# This file is part of TGSBot.
# Permission to copy or use is limited. Please see LICENSE for information.
#
"""Welcome message as login trigger and log in mechanics."""

import time
from twisted.python import log
from operation.basics import Request, Response
from logging import INFO

TRACE = 15
VERBOSE = 17

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
    def __init__(self, dispatch, manage, callback, expected="BOTUID"):
        self.expected = expected
        self.callback = callback
        self.label = 'LOGIN'
        Request.__init__(self, dispatch, manage,)
        # Add two more expected messages in case login fails!
        self.login_failed = "** User not known or wrong password."
        self.manage[self.login_failed] = self
        self.logged_in_already = "** Warning: You are already logged in."
        self.manage[self.logged_in_already] = self

    def received(self, message):
        first_line = message[0]
        log.msg(self.msg_tests % first_line, logLevel=VERBOSE)
        if first_line.startswith(self.expected):
            uid = first_line.split()[1]
            self.callback(uid)
        elif first_line == self.login_failed:
            self.dispatch.stop("login failed")
        elif first_line == self.logged_in_already:
            self.send_command(self.dispatch.login_sequence)
            del self.manage[self.login_failed]
        log.msg(self.msg_applies + '+'*40, logLevel=VERBOSE)
        time_used = time.time() - self.sent_request
        log.msg(self.msg_waited % time_used, logLevel=INFO)
        del message[0:1]
        if first_line.startswith(self.expected):
            self.purge()
            self.dispatch.login_hook()
        return True
