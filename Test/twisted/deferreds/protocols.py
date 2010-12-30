#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Das Script dient Testzwecken zum Thema 'twisted'.
Beispiel aus dem twisted-core.pdf Kap. 2.1.2
"""

from twisted.internet.protocol import Protocol
##from twisted.internet import defer
##from twisted.python import log

class Echo(Protocol):
    """Protocol Echo"""
    def dataReceived(self, data):
        print 'heard:', data
        self.transport.write('echo %s: %s\r\n' % (self.id,data))
        if data.startswith('exit'):
            print 'lasse die Verbindung %s fallen' % self.id
            self.transport.loseConnection()
        if data.startswith('change'):
            print 'wechsle das Protokoll zu Quiet'
            # So kommt man nicht in ein anderes Protokoll. Erst der nächste
            # bekommt das neue Protokoll untergejubelt.
            self.factory.protocol = Quiet

    def connectionMade(self):
        self.id = '(%s) %d' % (id(self),self.factory.incNumProtocols())
        msg = 'sei gegruesst, nummer %s\r\n' % self.id
        self.transport.write('server %s: %s' % (self.id, msg))
        print 'had %d connections so far :)' % self.factory.maxProtocols
        if self.factory.numProtocols > 2001:
            print 'wegen ueberfuellung geschlossen'
            self.transport.write("Too many connections, try later")
            self.transport.loseConnection()

    def connectionLost(self, reason):
        self.factory.decNumProtocols()
        print 'aus die maus', self.id

class Quiet(Echo):
    """Protocol Quiet"""
    def dataReceived(self, data):
        print 'heard:', data
        self.transport.write('quiet %s: %s\r\n' % (self.id, data))
        if data.startswith('exit'):
            print 'lasse die Verbindung %s fallen' % self.id
            self.transport.loseConnection()
        if data.startswith('change'):
            print 'wechsle das Protokoll zu Echo'
            self.factory.protocol = Echo
    
class QOTD(Protocol):
    def connectionMade(self):
        self.transport.write("An apple a day keeps the doctor away\r\n")
        self.transport.loseConnection()

class CLIP(Echo):
    def __init__(self,):
        self.brocken = ''
        
    def dataReceived(self, data):
        print 'received (%d) %s' % (len(data), data)
        if len(data) == 1:
            print 'puzzling (%s)' % data
            self.brocken = data
        elif len(self.brocken) == 1:
            data = self.brocken + data
            self.brocken = ''
        if len(data) > 1:
            print 'heard:', data
            if data.lower().startswith('quit'):
                print 'lasse die Verbindung %s fallen' % self.id
                self.transport.loseConnection()
            d = self.factory.parse(data)
            d.addCallback(self.transportResult)

    def transportResult(self, result):
        print 'transportRESULT', result
        self.transport.write('echo %s: %s\r\n' % (self.id, result))

    def message_from_deferred(self, msg):
        self.transport.write('deferred %s: %s\r\n' % (self.id, msg))
