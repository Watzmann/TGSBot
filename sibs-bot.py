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

TRACE = 15

import logging
logging.addLevelName(TRACE, 'TRACE')
##logging.basicConfig(level=logging.DEBUG,)
##print 'sibs-bot set logginglevel'

NICK = 'tigerI'

log.startLogging(open('/var/log/SIBS/bot/%s.log' % NICK, 'a'))
observer = log.PythonLoggingObserver()
observer.start()

class Com(Protocol):
    def dataReceived(self, rawdata):
        data = rawdata.rstrip('\r\n')
        self.dispatch.parse(data)

    def sendMessage(self, msg):
        log.msg('>> %s' % msg, logLevel=logging.INFO)
        self.transport.write(msg + '\r\n')

    def connectionMade(self,):
        log.msg('connectionMade', logLevel=TRACE)
        self.dispatch = Dispatch(self, NICK, 'hallo')

    def dropConnection(self,):
        log.msg('dropConnection', logLevel=TRACE)
        self.transport.loseConnection()

class ComClientFactory(ClientFactory):

    protocol = Com

    def startedConnecting(self, connector):
        log.msg('Started to connect.', logLevel=TRACE)
        #reactor.callLater(10, reactor.stop)

    def clientConnectionLost(self, connector, reason):
        log.msg('Lost connection. Reason: %s' % reason, logLevel=logging.INFO)
        reactor.callWhenRunning(reactor.stop)

    def clientConnectionFailed(self, connector, reason):
        log.msg('Connection failed. Reason: %s' % reason, logLevel=logging.INFO)
        reactor.callWhenRunning(reactor.stop)

factory = ComClientFactory()
reactor.connectTCP('localhost', 8081, factory)
reactor.run()
