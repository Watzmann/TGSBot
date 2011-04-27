#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Ein Twisted-Client als Entwicklungs-Hilfe/Tool für SIBS.
Basiert auf client/twisted-client1.py. Das Reconnecting-Zeugs ist raus.
"""

from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor
from sys import stdout

def communicate(protocol):
    """Do a bit of manual communication with the server. Quit with a keyword."""
    s = raw_input('give me some >> ')
    if s.lower() in ('bye', 'exit', 'quit'):
        reactor.stop()
    protocol.sendMessage(s)

class Com(Protocol):
    def dataReceived(self, data):
        stdout.write('RETURN: '+data)
        
    def sendMessage(self, msg):
        print 'in sendMessage with', msg
        self.transport.write("MESSAGE %s\r\n" % msg)
        reactor.callLater(1, communicate, self)

    def connectionMade(self,):
        print 'connectionMade'
        reactor.callLater(1, communicate, self)

class ComClientFactory(ClientFactory):
    def startedConnecting(self, connector):
        print 'Started to connect.'

    def buildProtocol(self, addr):
        print 'Connected.'
        return Com()

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection. Reason:', reason
##        reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        reactor.stop()

factory = ComClientFactory()
reactor.connectTCP('localhost', 8082, factory)
reactor.run()

#communicate(factory)
