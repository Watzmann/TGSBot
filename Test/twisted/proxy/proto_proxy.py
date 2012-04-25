#!/usr/bin/python
# -*- coding: utf-8 -*-
"""A twisted proxy to sniff communication between TiGa server and client."""

from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, ClientFactory
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
        reactor.stop()

    def dataReceived(self, data):
        stdout.write(data)

class ComClientFactory(ClientFactory):

    protocol = Com

    def __init__(self, direction):
        self.direction = direction

    def startedConnecting(self, connector):
        print self.direction, 'Started to connect.'

    def clientConnectionLost(self, connector, reason):
        print self.direction, 'Lost connection. Reason:', reason
        reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        print self.direction, 'Connection failed. Reason:', reason
        reactor.stop()

server = ClientFactory('server')
client = ClientFactory('client')

reactor.connectTCP("localhost", 8080, server)
reactor.connectTCP("localhost", 8082, client)
reactor.run()
