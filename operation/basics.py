#
# (c) Copyright 2012 Andreas Hausmann
# This file is part of TGSBot.
# Permission to copy or use is limited. Please see LICENSE for information.
#
"""Basic classes Request and Response for handling server commands."""

import time

class Request:
    def __init__(self, dispatch, manage,):
        self.dispatch = dispatch
        self.manage = manage
        self.update()
        # Some messages for use of inheriting classes
        self.msg_tests = '%s tests: %%s' % self.label
        self.msg_applies = '%s applies ' % self.label
        self.msg_waited = '%s waited for answer %%s seconds' % self.label

    def received(self, message):
        print 'got expected answer: >%s<' % message

    def update(self,):
        self.manage[self.expected] = self

    def purge(self,):
        for k,v in self.manage.items():
            if v == self:
                del self.manage[k]

    def send_command(self, command):
        self.dispatch.send_server(command)
        self.sent_request = time.time()

class Response:
    def __init__(self, answer):
        self.answer = (self.trivial, answer)

    def complex_answer(self, my_callable, expected):
        self.answer = (my_callable, expected)
        return self

    def trivial(self, expected, message):
        return expected == message

    def test(self, message):
        check, expected = self.answer
        return check(expected, message)

