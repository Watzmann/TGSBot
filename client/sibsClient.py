#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Ein Twisted-Client als Entwicklungs-Hilfe/Tool for SIBS.
Basiert auf client/twisted-client1.py. Das Reconnecting-Zeugs ist raus.
"""

from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.internet import reactor
from twisted.python import log

TRACE = 15
VERBOSE = 17

import logging

class Com(Protocol):
    def __init__(self, options, factory):
        self.options = options
        self.factory = factory

    def dataReceived(self, rawdata):
        data = rawdata.rstrip('\r\n')
        self.dispatch.parse(data)

    def sendMessage(self, msg):
        log.msg('>> %s' % msg, logLevel=logging.INFO)
        self.transport.write(msg + '\r\n')

    def connectionMade(self,):
        log.msg('connectionMade', logLevel=TRACE)
        user = self.options.user
        password = self.options.password
        self.dispatch = Dispatch(self, user, password)

    def dropConnection(self,):
        log.msg('dropConnection', logLevel=TRACE)
        self.transport.loseConnection()

class ComClientFactory(ReconnectingClientFactory):
    def startedConnecting(self, connector):
        log.msg('Started to connect.', logLevel=TRACE)

    def buildProtocol(self, addr):
        log.msg('Connected to %s:%s.' % (options.host, options.port), logLevel=TRACE)
        log.msg('Resetting reconnection delay.', logLevel=VERBOSE)
        self.resetDelay()
        return Com(self.options, self)

    def clientConnectionLost(self, connector, reason):
        log.msg('Lost connection. Reason: %s' % reason, logLevel=logging.INFO)
        if getattr(self, 'restart', True):
            ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
        else:
            log.msg('Done - no restart', logLevel=logging.INFO)
            reactor.callWhenRunning(reactor.stop)

    def clientConnectionFailed(self, connector, reason):
        log.msg('Connection failed. Reason: %s' % reason, logLevel=logging.INFO)
        if getattr(self, 'restart', True):
            ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
        else:
            log.msg('Done - no restart', logLevel=logging.INFO)
            reactor.callWhenRunning(reactor.stop)

    def stop(self,):
        self.restart = False
