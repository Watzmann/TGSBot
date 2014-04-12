# -*- coding: utf-8 -*-
#
# (c) Copyright 2014 Andreas Hausmann
# This file is part of TGSBot.
# Permission to copy or use is limited. Please see LICENSE for information.
#
"""Commands about playing the match."""

import sys
import time
from twisted.python import log
from twisted.internet import defer
from operation.basics import Request, Response

TRACE = 15
VERBOSE = 17

import logging
logging.addLevelName(TRACE, 'TRACE')
logging.addLevelName(VERBOSE, 'VERBOSE')

class Action:
    """Action objects here are meant to ask gnubg for the match winning chance
    (MWC) to support dropper handling of the server.
"""
    def __init__(self, order, parameters, gnubg, callback):
        log.msg('create action with (%s - %s)' % (order, parameters),
                                                        logLevel=logging.DEBUG)
        self.gnubg = gnubg
        self.callback = callback
        {'evaluate': self._evaluate,  # evaluate a match situation
         }[order](parameters)

    def _evaluate(self, parameters):
        self.oracle = self.gnubg.ask_gnubg('evaluate: %s' % parameters[0])
        log.msg('got DOUBLE oracle: %s' % self.oracle, logLevel=logging.DEBUG)
        if not self.oracle is None:
            self.oracle.addCallback(self.callback)

class Turn(Request):
    """A Turn() represents one turn in a game of backgammon. The server will
    notify the bot of a turn to take. That notification is introduced by the
    bot unique id (bot_uid) and comprises a 'command' and parameters.
    An action has to be taken according to the given command.

    # TODO: Beispiel von solchen Messages!
"""
    def __init__(self, dispatch, manage,):
        self.gnubg = dispatch.get_gnubg()
        self.expected = dispatch.bot_uid
        self.direction = dispatch.direction
        self._callback = {'evaluate': self.send_evaluate,
                         }
        self.label = ''
        self.sent_request = time.time()
        Request.__init__(self, dispatch, manage,)

    def send_evaluate(self, double):
        log.msg('got move: %s' % move, logLevel=logging.DEBUG)
        # No resign decision here. See Action._move() above.
        if self.direction == '+':
            mv = ' '.join(['m',] + \
                        [str(25-int(m)) for m in move.strip('()').split(',')])
        else:
            mv = ' '.join(['m',] + move.strip('()').split(','))
        self.send_command(mv)
        self.purge()

    def received(self, message):
        log.msg(self.msg_tests % message[0], logLevel=VERBOSE)
        expected_reaction = message[0].split()
        ret = len(expected_reaction) > 2
        if ret:
            uid, order = expected_reaction[:2]
            parameters = expected_reaction[2:]
            callback = self._callback[order]
            self.sent_action = time.time()
            self.action = Action(order, parameters, self.gnubg, callback)
            log.msg(self.msg_applies + '+'*40, logLevel=VERBOSE)
            time_used = time.time() - self.sent_request
            log.msg(self.msg_waited % time_used, logLevel=logging.INFO)
            Turn(self.dispatch, self.manage,)
            del message[0]
        else:
            log.msg('TURN applies NOT '+'-'*36, logLevel=VERBOSE)
        return ret
