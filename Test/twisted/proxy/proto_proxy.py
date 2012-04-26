#!/usr/bin/python
# -*- coding: utf-8 -*-
"""A twisted proxy to sniff communication between TiGa server and client."""

from twisted.internet import reactor, defer
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.web import http
from twisted.internet.error import ReactorNotRunning
from datetime import date

class Com(Protocol):

    def sendMessage(self, msg):
        self.transport.write("%s" % msg)

    def connectionMade(self):
        if self.factory.side == 'client':
            print 'client connected'
        self.factory.partner.receiver = self.sendMessage
        self.factory.is_listening = True
        self.buffer = []

    def connectionLost(self, reason):
        if self.factory.side != 'client':
            return
        print 'client Lost connection. Reason:', reason
        try:
            reactor.stop()
        except ReactorNotRunning:
            pass

    def dataReceived(self, data):
        self.factory.sniffer.write(self.factory.separator)
        self.factory.sniffer.write(data)
        self.factory.sniffer.flush()
        if self.factory.partner.is_listening:
            self.factory.receiver(data)
        else:
            self.buffer += data

class ComServerFactory(http.HTTPFactory):
    # TODO: have a look: is HTTPFactory precisely what you need??

    protocol = Com
    is_listening = False
    
    def __init__(self, sniffer):
        self.side = 'client'
        self.separator = '%s server\n' % ('>'*75,)
        self.sniffer = sniffer

    def clientConnectionFailed(self, connector, reason):
        print self.side, 'Connection failed. Reason:', reason
        try:
            reactor.stop()
        except ReactorNotRunning:
            pass

class ComClientFactory(ClientFactory):

    protocol = Com
    is_listening = False

    def __init__(self, sniffer):
        self.side = 'server'
        self.separator = '%s client\n' % ('<'*75,)
        self.sniffer = sniffer

    def startedConnecting(self, connector):
        print self.side, 'Started to connect.'

    def clientConnectionLost(self, connector, reason):
        print self.side, 'Lost connection. Reason:', reason
        try:
            reactor.stop()
        except ReactorNotRunning:
            pass

    def clientConnectionFailed(self, connector, reason):
        print self.side, 'Connection failed. Reason:', reason
        try:
            reactor.stop()
        except ReactorNotRunning:
            pass


sniff_file = open('proxy.log', 'a')
sniff_file.write('\n\n\n%s %s\n' % ('='*75, date.today().ctime()))
server = ComClientFactory(sniff_file)
client = ComServerFactory(sniff_file)
server.partner = client
client.partner = server

reactor.connectTCP("localhost", 8081, server)
reactor.listenTCP(8082, client)
reactor.run()
sniff_file.close()
