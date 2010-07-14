#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Ein Twisted-Client zu Testzwecken zum Thema 'twisted'.
Siehe twisted-core.pdf, Kap. 2.2.
"""

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientCreator
from sys import stdout

class Greeter(Protocol):
    def sendMessage(self, msg):
        self.transport.write("MESSAGE %s\n" % msg)

    def connectionLost(self, reason):
        reactor.stop()

    def dataReceived(self, data):
        stdout.write(data)

def communicate(p):
    while True:
        s = raw_input('give me more ')
        if s.lower() in ('bye', 'exit', 'quit'):
            break
        p.sendMessage(s)

def gotProtocol(p):
    p.sendMessage("Hello")
    reactor.callLater(1, p.sendMessage, "This is sent in a second")
    communicate(p)
    reactor.callLater(2, p.transport.loseConnection)

c = ClientCreator(reactor, Greeter)
c.connectTCP("localhost", 8080).addCallback(gotProtocol)
reactor.run()
