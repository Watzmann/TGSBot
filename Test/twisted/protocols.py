#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Das Script dient Testzwecken zum Thema 'twisted'.
Beispiel aus dem twisted-core.pdf Kap. 2.1.2
"""

from twisted.internet.protocol import Protocol
##from twisted.python import log

class Echo(Protocol):
    def dataReceived(self, data):
        print 'heard:', data
        self.transport.write('echo: ' + data + '\r\n')
        if data.startswith('exit'):
            print 'lasse die Verbindung fallen'
            self.transport.loseConnection()

    def connectionMade(self):
        self.factory.numProtocols = self.factory.numProtocols+1
        msg = 'sei gegruesst, nummer %d\r\n' % self.factory.numProtocols
        print msg
        self.transport.write('server: ' + msg)
        if self.factory.numProtocols > 100:
            self.transport.write("Too many connections, try later")
            self.transport.loseConnection()

    def connectionLost(self, reason):
        self.factory.numProtocols = self.factory.numProtocols-1
        print 'aus die maus', self.factory.numProtocols

class QOTD(Protocol):
    def connectionMade(self):
        self.transport.write("An apple a day keeps the doctor away\r\n")
        self.transport.loseConnection()
