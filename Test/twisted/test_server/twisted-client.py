#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Ein Twisted-Client als Entwicklungs-Hilfe/Tool für SIBS.
Basiert auf client/twisted-client1.py. Das Reconnecting-Zeugs ist raus.
"""

from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor
from sys import stdout

class Com(Protocol):
    def dataReceived(self, data):
        stdout.write('RETURN: '+data)

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

reactor.connectTCP('localhost', 8082, ComClientFactory())
reactor.run()
