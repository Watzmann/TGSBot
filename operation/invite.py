#
# (c) Copyright 2012 Andreas Hausmann
# This file is part of TGSBot.
# Permission to copy or use is limited. Please see LICENSE for information.
#
"""Enable bot to invite other players (i.e. other bots)."""

import random
import time
from twisted.python import log
from twisted.internet import defer
from operation.basics import Request, Response
from operation.play import Play

TRACE = 15
VERBOSE = 17

import logging
logging.addLevelName(TRACE, 'TRACE')
logging.addLevelName(VERBOSE, 'VERBOSE')

class Bots(Request):
    def __init__(self, dispatch, manage, callback):
        self.expected = "Playing bots:"
        self.label = 'BOTS'
        Request.__init__(self, dispatch, manage,)
        self.answer = defer.Deferred()
        self.answer.addCallback(callback)
        self.send_command('show bots_ready')

    def received(self, message):
        self.settings = {}
        log.msg(self.msg_tests % message[0], logLevel=VERBOSE)
        try:
            idx = message.index('')
            bots = message[1:idx]
            del message[:idx+1]
        except ValueError:
            bots = message[1:]
            del message[:]
        log.msg('BOTS: bots present: %s' % bots, logLevel=logging.DEBUG)
        self.answer.callback(bots)
        log.msg(self.msg_applies + '+'*40, logLevel=VERBOSE)
        time_used = time.time() - self.sent_request
        log.msg(self.msg_waited % time_used, logLevel=logging.INFO)
        self.purge()
        return True

class Join(Request):
    message_new = {0: "** You are now playing a %s point match with %s.",
                   1: "** You are now playing an unlimited match with %s.",
                   2: "** Player %s has joined you for a %s point match.",
                   3: "** Player %s has joined you for an unlimited match.",
                   }
    message_resume = {0: "You are now playing with %s. " \
                                        "Your running match was loaded.",
                      1: "You are now playing with %s. " \
                                        "Your running match was loaded.",
                      2: "%s has joined you. Your running match was loaded.",
                      3: "%s has joined you. Your running match was loaded.",
                      }
    ordered_arguments = {0: lambda a,b: (a,b),
                         2: lambda a,b: (b,a),
                         }

    def __init__(self, dispatch, manage, opp, ML, type_of_invitation):
        self.opponent = opp
        self.ML = ML
        self.expected = self.expected_answer(opp, ML, type_of_invitation)
        self.busy = Busy(dispatch, manage, opp, self.expected)
        self.variation = 'standard'
        self.label = 'JOIN'
        Request.__init__(self, dispatch, manage,)

    def expected_answer(self, opponent, ML, type_of_invitation):
        if ML is None:
            i_expect = self.message_resume[type_of_invitation] % opponent
            self.resume = True
        elif ML == 'unlimited':
            i_expect = self.message_new[type_of_invitation] % opponent
            self.resume = False
        else:
            i_expect = self.message_new[type_of_invitation] % \
                       self.ordered_arguments[type_of_invitation](ML, opponent)
            self.resume = False
        return i_expect

    def received(self, message):
        log.msg(self.msg_tests % message[0], logLevel=VERBOSE)
        line = message[0].split()
        direction = line.pop()
        my_line = ' '.join(line)
        expected_answer = self.expected == my_line
        if expected_answer:
            log.msg(self.msg_applies + '+'*40, logLevel=VERBOSE)
            time_used = time.time() - self.sent_request
            log.msg(self.msg_waited % time_used, logLevel=logging.INFO)
            if direction in ('(-)', '(+)'):
                self.dispatch.direction = direction.strip('()')
            else:
                self.dispatch.direction = '+'
            greetings = 'Hello! Enjoy this match. Good luck.'
            self.send_command('tell %s %s' % (self.opponent, greetings))
            self.purge()
            self.busy.purge()
            self.dispatch.opponent = self.opponent
            self.dispatch.saved = Saved(self.dispatch, self.manage, self.opponent)
            Play(self.dispatch, self.manage, self.opponent, self.ML,
                                resume=self.resume, variation=self.variation)
            del message[0]
        else:
            log.msg('JOIN applies NOT '+'-'*36, logLevel=VERBOSE)
        return expected_answer

class Busy(Request):
    def __init__(self, dispatch, manage, opponent, invitation):
        self.refusal1 = "** %s is already playing with someone else." % opponent
        self.refusal2 = "** There's no saved match with %s. " \
                                        "Please give a match length." % opponent
        self.invitation = invitation
        self.label = 'BUSY'
        self.sent_request = time.time()
        Request.__init__(self, dispatch, manage,)

    def received(self, message):
        log.msg(self.msg_tests % message[0], logLevel=VERBOSE)
        if self.invitation in self.manage:
            del self.manage[self.invitation]
        log.msg(self.msg_applies + '+'*40, logLevel=VERBOSE)
        time_used = time.time() - self.sent_request
        log.msg(self.msg_waited % time_used, logLevel=logging.INFO)
        self.purge()
        del message[0]
        self.dispatch.relax_hook()
        return True

    def update(self,):
        self.manage[self.refusal1] = self
        self.manage[self.refusal2] = self

class Saved(Request):
    def __init__(self, dispatch, manage, opponent):
        self.expected = "** Player %s has left the game. " \
                                            "The game was saved." % opponent
        self.label = 'SAVED'
        Request.__init__(self, dispatch, manage,)

    def received(self, message):
        log.msg(self.msg_tests % message[0], logLevel=VERBOSE)
        log.msg(self.msg_applies + '+'*40, logLevel=VERBOSE)
        self.purge()
        del self.dispatch.saved
        del message[0]
        self.dispatch.relax_hook()
        return True

def invite_bots(dispatch):
    def invite_one(bots):
        ML = random.choice((1,3,5,7,9))
        if dispatch.user in bots:
            bots.remove(dispatch.user)
        if len(bots) > 0:
            opponent = random.choice(bots)
            invite(dispatch, opponent, ML)
        else:
            dispatch.relax_hook()

    bots = Bots(dispatch, dispatch.requests, invite_one)

def join(dispatch, opponent, ML, type_of_invitation=0):
    join = Join(dispatch, dispatch.requests, opponent, ML, type_of_invitation)
    if type_of_invitation in (0, 1):
        join.send_command('join %s' % opponent)
    return join

def invite(dispatch, opponent, ML):
    ret = Join(dispatch, dispatch.requests, opponent, ML, 2)
    if ML is None:
        ret.send_command('invite %s' % opponent)
    else:
        ret.send_command('invite %s %s' % (opponent, ML))
