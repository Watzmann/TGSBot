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
        self.transport.write('echo %d: %s\r\n' % (self.id,data))
        if data.startswith('exit'):
            print 'lasse die Verbindung %d fallen' % self.id
            self.transport.loseConnection()

    def connectionMade(self):
        self.id = self.factory.numProtocols = self.factory.numProtocols+1
        msg = 'sei gegruesst, nummer %d\r\n' % self.id
        print msg
        self.transport.write('server %d: %s' % (self.id,msg))
        if self.factory.numProtocols > 1001:
            print 'wegen ueberfuellung geschlossen'
            self.transport.write("Too many connections, try later")
            self.transport.loseConnection()

    def connectionLost(self, reason):
        self.factory.numProtocols = self.factory.numProtocols-1
        print 'aus die maus', self.id

class QOTD(Protocol):
    def connectionMade(self):
        self.transport.write("An apple a day keeps the doctor away\r\n")
        self.transport.loseConnection()
