#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Ein Twisted-Client als Entwicklungs-Hilfe/Tool für SIBS.
Basiert auf client/twisted-client1.py. Das Reconnecting-Zeugs ist raus.
"""

from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor, defer
from sys import stdout
import random
from bot_client import Dispatch

VERBOSE = True

MESSAGES = (('shout', 'Ich bin heute mal hier!'), 
            ('shout', 'Ist Gustav da?'),
            ('shout', 'Do you have a cookie?'),
            ('shout', 'Where is Patti?'),
            ('shout', 'Spielt jemand mit mir'),
            ('tell', 'hannes Schau mal an'),
            ('tell', 'andreas das hab ich dem hannes auch gesagt.'),
            ('tell', '####### das wollt ich auch sagen.'),
            )

class Com(Protocol):
    def dataReceived(self, rawdata):
        data = rawdata.rstrip('\r\n')
        self.dispatch.parse(data)

    def sendMessage(self, msg):
        print '>>', msg
        self.transport.write(msg + '\r\n')

    def connectionMade(self,):
        print 'connectionMade'
        self.dispatch = Dispatch(self, 'tigerI', 'hallo')

    def dropConnection(self,):
        print 'dropConnection'
        self.transport.loseConnection()

class ComClientFactory(ClientFactory):

    protocol = Com

    def startedConnecting(self, connector):
        print 'Started to connect.'

##    def buildProtocol(self, addr):
##        print 'Connected.'
##        return Com()

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection. Reason:', reason
        reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        reactor.stop()

factory = ComClientFactory()
reactor.connectTCP('localhost', 8081, factory)
reactor.run()
