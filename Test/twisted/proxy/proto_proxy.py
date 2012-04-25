#!/usr/bin/python
# -*- coding: utf-8 -*-
"""A twisted proxy to sniff communication between TiGa server and client."""

from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.web import http
from twisted.internet.error import ReactorNotRunning
from sys import stdout

class Com(Protocol):
    def sendMessage(self, msg):
        print 'in sendMessage with', msg
        self.transport.write("MESSAGE %s\n" % msg)

    def connectionLost(self, reason):
        # Damit wird der reactor beendet; sonst würde das Ding endlos laufen
        # connectionLost ist der richtige Zeitpunkt; macht man es z.B. in
        # gotProtocol(), dann würden die 'callLater'-Aufrufe auch beendet, also
        # nicht ausgeführt werden.
        pass #reactor.stop()

    def dataReceived(self, data):
        stdout.write(data)

class ComServerFactory(http.HTTPFactory):
    # TODO: have a look: is HTTPFactory precisely what you need??

    protocol = Com
    
    def __init__(self,):
        self.direction = 'client'

    def startedConnecting(self, connector):
        print self.direction, 'Started to connect.'

    def clientConnectionLost(self, connector, reason):
        print self.direction, 'Lost connection. Reason:', reason
        try:
            reactor.stop()
        except ReactorNotRunning:
            pass

    def clientConnectionFailed(self, connector, reason):
        print self.direction, 'Connection failed. Reason:', reason
        try:
            reactor.stop()
        except ReactorNotRunning:
            pass

class ComClientFactory(ClientFactory):

    protocol = Com

    def __init__(self,):
        self.direction = 'server'

    def startedConnecting(self, connector):
        print self.direction, 'Started to connect.'

    def clientConnectionLost(self, connector, reason):
        print self.direction, 'Lost connection. Reason:', reason
        try:
            reactor.stop()
        except ReactorNotRunning:
            pass

    def clientConnectionFailed(self, connector, reason):
        print self.direction, 'Connection failed. Reason:', reason
        try:
            reactor.stop()
        except ReactorNotRunning:
            pass

server = ComClientFactory()
client = ComServerFactory()

reactor.connectTCP("localhost", 8081, server)
reactor.listenTCP(8082, client)
reactor.run()
