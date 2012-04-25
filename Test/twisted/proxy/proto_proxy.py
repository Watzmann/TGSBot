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

    def connectionMade(self):
        if self.factory.direction == 'client':
            print 'client connected'
        self.factory.partner.receiver = self.sendMessage
        self.factory.is_listening = True
        self.buffer = []

    def connectionLost(self, reason):
        if self.factory.direction != 'client':
            return
        print 'client Lost connection. Reason:', reason
        try:
            reactor.stop()
        except ReactorNotRunning:
            pass

    def dataReceived(self, data):
#        stdout.write('From %s heard:' % self.factory.direction)
#        stdout.write(data)
        if self.factory.partner.is_listening:
            self.factory.receiver(data)
        else:
            self.buffer += data

class ComServerFactory(http.HTTPFactory):
    # TODO: have a look: is HTTPFactory precisely what you need??

    protocol = Com
    is_listening = False
    
    def __init__(self,):
        self.direction = 'client'

    def clientConnectionFailed(self, connector, reason):
        print self.direction, 'Connection failed. Reason:', reason
        try:
            reactor.stop()
        except ReactorNotRunning:
            pass

class ComClientFactory(ClientFactory):

    protocol = Com
    is_listening = False

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
server.partner = client
client.partner = server

reactor.connectTCP("localhost", 8081, server)
reactor.listenTCP(8082, client)
reactor.run()
