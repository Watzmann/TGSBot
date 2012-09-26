# -*- coding: utf-8 -*-

from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.internet import reactor, defer
from twisted.python import log
import sys

GNUBG = 8083
TRACE = 15
VERBOSE = 17

import logging
logging.addLevelName(TRACE, 'TRACE')
logging.addLevelName(VERBOSE, 'VERBOSE')

class Bridge:
    def __init__(self,):
        self.gnubg = None
        self.bot = None

    def set_gnubg(self, gnubg_com):
        """Set a protocol object to communicate with gnubg."""
        self.gnubg = gnubg_com

    def set_bot(self, bot_com):
        """Set an object to communicate with bot."""
        self.bot = bot_com

bot_gnubg_bridge = Bridge()

class Com(Protocol): # TODO: LineReceiver

    def __init__(self,):
        self.custom_question = {
            'bestMove': self._best_move,
            'double': self._double,
            'take': self._take,
            }

    def dataReceived(self, rawdata):
        data = rawdata.rstrip('\r\n')
        self.answer.callback(data)

    def sendMessage(self, msg):
        log.msg('>> %s' % msg, logLevel=logging.INFO)
        self.transport.write(msg + '\r\n')

    def connectionMade(self,):
        log.msg('connectionMade', logLevel=TRACE)
        self.bridge = bot_gnubg_bridge
        bot_gnubg_bridge.set_gnubg(self)
        self.bridge = bot_gnubg_bridge

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
        mid, pid = match_id.split(':')
        if len(arguments) > 1 and arguments[1] == 'resign':
             self.sendMessage('opt:consider resign')
        self.sendMessage('mid:%s' % mid)
        self.sendMessage('pid:%s' % pid)
        self.sendMessage('cmd:double')

    def _take(self, question):
        log.msg('question: %s' % question, logLevel=logging.DEBUG)
        mid, pid = question.split(':')
        self.sendMessage('mid:%s' % mid)
        self.sendMessage('pid:%s' % pid)
        self.sendMessage('cmd:take')

class ComClientFactory(ReconnectingClientFactory):
    def startedConnecting(self, connector):
        log.msg('Started to connect.', logLevel=TRACE)

    def buildProtocol(self, addr):
        log.msg('Connected to %s:%s.' % (self.host, self.port), logLevel=TRACE)
        log.msg('Resetting reconnection delay.', logLevel=VERBOSE)
        self.resetDelay()
        return Com()

    def clientConnectionLost(self, connector, reason):
        log.msg('Lost connection. Reason: %s' % reason, logLevel=logging.INFO)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        log.msg('Connection failed. Reason: %s' % reason, logLevel=logging.INFO)
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

def set_up_gnubg(host='localhost', port=GNUBG):
    factory = ComClientFactory()
    factory.host = host
    factory.port = port
    reactor.connectTCP(host, port, factory)
    return bot_gnubg_bridge
