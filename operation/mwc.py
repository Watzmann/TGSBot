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
        {'evalMWC': self._evaluate,  # evaluate a match situation
         }[order](parameters)

    def _evaluate(self, parameters):
        self.oracle = self.gnubg.ask_gnubg('evalMWC: %s' % parameters[0])
        log.msg('got EVALMWC oracle: %s' % self.oracle, logLevel=logging.DEBUG)
        if not self.oracle is None:
            self.oracle.addCallback(self.callback)

class MWC(Request):
    """An MWC() represents one evaluation of a game of backgammon.
    The server will ask for an evaluation of a match_id/position_id pair.
    That request is introduced by the bot unique id (bot_uid).

    # TODO: Beispiel von solchen Messages!
"""
    def __init__(self, dispatch, manage,):
        self.gnubg = dispatch.get_gnubg()
        self.expected = dispatch.bot_uid
        self._callback = {'evalMWC': self.send_evaluate,
                         }
        self.label = 'MWC'
        Request.__init__(self, dispatch, manage,)

    def send_evaluate(self, result):
        time_used = time.time() - self.sent_request
        log.msg(self.msg_waited % time_used, logLevel=logging.INFO)
        log_msg = 'got mwc for %s: %s' % (self.gid, result)
        log.msg(log_msg, logLevel=logging.DEBUG)
        mwc = 'evaluate %s %s' % (self.gid, result)
        self.send_command(mwc)
        self.purge()

    def received(self, message):
        log.msg(self.msg_tests % message[0], logLevel=VERBOSE)
        expected_reaction = message[0].split()
        ret = len(expected_reaction) > 2
        if ret:
            uid, order, self.gid = expected_reaction[:3]
            parameters = expected_reaction[3:]
            callback = self._callback[order]
            self.sent_action = time.time()
            self.action = Action(order, parameters, self.gnubg, callback)
            self.sent_request = time.time()
            log.msg(self.msg_applies + '+'*40, logLevel=VERBOSE)
            MWC(self.dispatch, self.manage,)
            del message[0]
        else:
            log.msg('MWC applies NOT '+'-'*36, logLevel=VERBOSE)
        return ret

class Register(Request):
    """Register takes care of completing registration as an evaluation bot.
    This is mainly to have the server send pending calls after bot login.
    It gives the server sufficient time for an answer.
"""
    def __init__(self, dispatch, manage):
        self.expected = "** Registered you as 'mwcEvaluation'"
        self.label = 'REGISTER'
        Request.__init__(self, dispatch, manage,)

    def received(self, message):
        first_line = message[0]
        log.msg(self.msg_tests % first_line, logLevel=VERBOSE)
        log.msg(self.msg_applies + '+'*40, logLevel=VERBOSE)
        time_used = time.time() - self.sent_request
        log.msg(self.msg_waited % time_used, logLevel=logging.INFO)
        del message[0:1]
        self.purge()
        self.send_command('send pending-mwcEvaluation')
        return True
