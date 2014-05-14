# -*- coding: utf-8 -*-
#
# (c) Copyright 2012 Andreas Hausmann
# This file is part of TGSBot.
# Permission to copy or use is limited. Please see LICENSE for information.
#

import sys
import os

from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.internet.error import ConnectError
from twisted.internet import reactor, defer
from twisted.python import log

GNUBG = 8083
HYPERBG = 8084
TRACE = 15
VERBOSE = 17

import logging
logging.addLevelName(TRACE, 'TRACE')
logging.addLevelName(VERBOSE, 'VERBOSE')

class Bridge:
    def __init__(self,):
        self.gnubg = {}
        self.bot = None

    def set_gnubg(self, gnubg_com, variation):
        """Set a protocol object to communicate with gnubg."""
        self.gnubg[variation] = gnubg_com

    def set_bot(self, bot_com):
        """Set an object to communicate with bot."""
        self.bot = bot_com

bot_gnubg_bridge = Bridge()

class Com(Protocol): # TODO: LineReceiver

    def __init__(self, variation):
        self.uid = None
        self.variation = variation
        self.custom_question = {
            'bestMove': self._best_move,
            'double': self._double,
            'take': self._take,
            'accept': self._accept,
            'evalMWC': self._evaluate,
            }

    def dataReceived(self, rawdata):
        data = rawdata.rstrip('\r\n')
        self.answer.callback(data)

    def sendMessage(self, msg):
        log.msg('>> %s' % msg, logLevel=logging.INFO)
        self.transport.write(msg + '\r\n')

    def connectionMade(self,):
        log.msg('connectionMade (%s)' % self.variation, logLevel=TRACE)
        self.bridge = bot_gnubg_bridge
        self.bridge.set_gnubg(self, self.variation)
        self.bridge.bot.set_bot_uid()
        if hasattr(self.bridge.bot, 'pending_action'):
            self.bridge.bot.pending_action.redo()

    def dropConnection(self,):
        log.msg('dropConnection', logLevel=TRACE)
        self.transport.loseConnection()

    def ask_gnubg(self, question):
        """ask_gnubg() takes a commandline of the form
        blablabla
    and returns a deferred to fire the answer.
    The command is referred to a gnubg server running on port xxxxxx
"""
        args = question.split(':')
        command = args[0]
        parameters = ':'.join(args[1:]).lstrip()
        self.custom_question[command](parameters)
        self.answer = defer.Deferred()
        return self.answer

    def _best_move(self, question):
        log.msg('question: %s' % question, logLevel=logging.DEBUG)
        arguments = question.split()
        mid, pid = arguments[0].split(':')
        nr_pieces = arguments[1]
        self.sendMessage('uid:%s' % self.uid)
        if len(arguments) > 2 and arguments[2] == 'resign':
             self.sendMessage('opt:consider resign')
        self.sendMessage('mid:%s' % mid)
        self.sendMessage('pid:%s' % pid)
        self.sendMessage('nrp:%s' % nr_pieces)
        self.sendMessage('cmd:bestMove')

    def _double(self, question):
        log.msg('question: %s' % question, logLevel=logging.DEBUG)
        arguments = question.split()
        match_id = arguments[0]
        self.sendMessage('uid:%s' % self.uid)
        mid, pid = match_id.split(':')
        if len(arguments) > 1 and arguments[1] == 'resign':
             self.sendMessage('opt:consider resign')
        self.sendMessage('mid:%s' % mid)
        self.sendMessage('pid:%s' % pid)
        self.sendMessage('cmd:double')

    def _take(self, question):
        log.msg('question: %s' % question, logLevel=logging.DEBUG)
        self.sendMessage('uid:%s' % self.uid)
        mid, pid = question.split(':')
        self.sendMessage('mid:%s' % mid)
        self.sendMessage('pid:%s' % pid)
        self.sendMessage('cmd:take')

    def _accept(self, question):
        log.msg('question: %s' % question, logLevel=logging.DEBUG)
        arguments = question.split()
        match_id = arguments[0]
        mid, pid = match_id.split(':')
        self.sendMessage('uid:%s' % self.uid)
        self.sendMessage('mid:%s' % mid)
        self.sendMessage('pid:%s' % pid)
        self.sendMessage('opt:%s' % arguments[1])
        self.sendMessage('cmd:accept')

    def _evaluate(self, question):
        log.msg('question: %s' % question, logLevel=logging.DEBUG)
        self.sendMessage('uid:%s' % self.uid)
        mid, pid = question.split(':')
        self.sendMessage('mid:%s' % mid)
        self.sendMessage('pid:%s' % pid)
        self.sendMessage('cmd:evalMWC')

    def set_uid_and_strength(self, uid, strength):
        log.msg('setting bot strength: %s' % strength, logLevel=logging.DEBUG)
        self.uid = uid
        self.sendMessage('uid:%s' % uid)
        self.sendMessage('opt:%s' % strength)
        self.sendMessage('cmd:set_player')

class ComClientFactory(ReconnectingClientFactory):
    def __init__(self, variation):
        self.variation = variation

    def startedConnecting(self, connector):
        log.msg('Started to connect to gnubg.', logLevel=TRACE)
        self.running = True

    def buildProtocol(self, addr):
        log.msg('Connected to %s:%s.' % (self.host, self.port), logLevel=TRACE)
        log.msg('Resetting reconnection delay.', logLevel=VERBOSE)
        self.resetDelay()
        return Com(self.variation)

    def clientConnectionLost(self, connector, reason):
        log.msg('Lost connection (%s). Reason: %s' % (self.variation, reason),
                                                          logLevel=logging.INFO)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
        self.yelp()

    def clientConnectionFailed(self, connector, reason):
        log.msg('Connection failed (%s). Reason: %s' % (self.variation, reason),
                                                          logLevel=logging.INFO)
        self.running = False
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
        self.yelp()

    def yelp(self,):
        """Setting a semaphore about missing connection. This should signal
    need for help to a monitoring tool.
"""
        if not hasattr(self, 'semaphore'):
            self.semaphore = Semaphore()

class Semaphore:

    _sem_path = ".semaphores"

    def __init__(self,):
        _sem_name = "1"
        fpath = os.path.join(self._sem_path, _sem_name)
        self._semaphore = open(fpath, 'w')
        self._semaphore.close()

def set_up_gnubg(variation, host='localhost', port=GNUBG, strength='supremo'):
    factory = ComClientFactory(variation)
    factory.host = host
    factory.port = port
    log.msg('About to connect to %s:%s.' % (host, port), logLevel=TRACE)
    reactor.connectTCP(host, port, factory)
    if factory.running:
        return bot_gnubg_bridge
    else:
        return None
