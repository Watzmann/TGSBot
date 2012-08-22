#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Ein Twisted-Client als Entwicklungs-Hilfe/Tool für SIBS.
Basiert auf client/twisted-client1.py. Das Reconnecting-Zeugs ist raus.
"""

from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor, defer
from twisted.python import log
import sys
import random
from operation.client import Dispatch

GNUBG = 8083
TRACE = 15

import logging
logging.addLevelName(TRACE, 'TRACE')

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
            'bestMove': self.best_move,
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
        command = question.split(':')
        self.custom_question[command[0]](':'.join(command[1:]).lstrip())
        self.answer = defer.Deferred()
        return self.answer

    def best_move(self, question):
        log.msg('question: %s' % question, logLevel=logging.DEBUG)
        match_id, nr_pieces = question.split()
        mid, pid = match_id.split(':')
        self.sendMessage('mid:%s' % mid)
        self.sendMessage('pid:%s' % pid)
        self.sendMessage('nrp:%s' % nr_pieces)
        self.sendMessage('cmd:bestMove')

class ComClientFactory(ClientFactory):

    protocol = Com

    def startedConnecting(self, connector):
        log.msg('Started to connect.', logLevel=TRACE)

    def clientConnectionLost(self, connector, reason):
        log.msg('Lost connection. Reason: %s' % reason, logLevel=logging.INFO)
        reactor.callWhenRunning(reactor.stop)

# TODO: muss reconnecting client sein

    def clientConnectionFailed(self, connector, reason):
        log.msg('Connection failed. Reason: %s' % reason, logLevel=logging.INFO)
        reactor.callWhenRunning(reactor.stop)

def set_up_gnubg(host='localhost', port=GNUBG):
    reactor.connectTCP(host, port, ComClientFactory())
    return bot_gnubg_bridge
