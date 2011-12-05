#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Ein Twisted-Client als Entwicklungs-Hilfe/Tool für SIBS.
Basiert auf client/twisted-client1.py. Das Reconnecting-Zeugs ist raus.
"""

from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor, defer
from sys import stdout
import random

MESSAGES = ('shout ' + 'Ich bin heute mal hier!',
            'shout ' + 'Ist Gustav da?',
            'shout ' + 'Do you have a cookie?',
            'shout ' + 'Where is Patti?',
            'shout ' + 'Spielt jemand mit mir',
            )

def communicate(protocol):
    """Do a bit of manual communication with the server. Quit with a keyword."""
    protocol.waiting_for_input = True
    s = raw_input('give me some >> ')
    protocol.waiting_for_input = False
    if s.lower() in ('bye', 'quit'):
        protocol.dropConnection()
    protocol.sendMessage(s)

def randomMessage(protocol):
    """Do a bit of random communication with the server."""
    msg = random.choice(MESSAGES)
    protocol.sendMessage(msg)

class Com(Protocol):
    def dataReceived(self, data):
        stdout.write('RETURN: '+data)
        
    def sendMessage(self, msg):
        print 'in sendMessage with', msg
        self.transport.write(msg + '\r\n')
        reactor.callLater(1, randomMessage, self)
        if not self.waiting_for_input:
            reactor.callLater(0.1, communicate, self)

    def connectionMade(self,):
        print 'connectionMade'
        reactor.callLater(0.2, randomMessage, self)
        reactor.callLater(0.1, communicate, self)

    def dropConnection(self,):
        print 'dropConnection'
        self.transport.loseConnection()

class ComClientFactory(ClientFactory):
    def startedConnecting(self, connector):
        print 'Started to connect.'

    def buildProtocol(self, addr):
        print 'Connected.'
        return Com()

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection. Reason:', reason
        reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        reactor.stop()

factory = ComClientFactory()
reactor.connectTCP('localhost', 8081, factory)
reactor.run()

#communicate(factory)
