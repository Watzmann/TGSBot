#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Ein Twisted-Client zu Testzwecken zum Thema 'twisted'.
Siehe twisted-core.pdf, Kap. 2.2.
"""

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientCreator
from sys import stdout

class Echo(Protocol):
    def dataReceived(self, data):
        stdout.write(data)

##This is one of the simplest protocols. It simply writes to standard output
##whatever it reads from the connection.
##There are many events it does not respond to. Here is an example of a
##Protocol responding to another event.
##from twisted.internet.protocol import Protocol
class WelcomeMessage(Protocol):
    def connectionMade(self):
        self.transport.write("Hello server, I am the client!\r\n")
        self.transport.loseConnection()

class Greeter(Protocol):
    def sendMessage(self, msg):
        print 'in sendMessage with', msg
        self.transport.write("MESSAGE %s\n" % msg)

    def connectionLost(self, reason):
        print 'lost connection for', reason
        reactor.stop()

    def dataReceived(self, data):
        stdout.write(data)

def gotProtocol(p):
    p.sendMessage("Hello")
    reactor.callLater(1, p.sendMessage, "This is sent in a second")
    reactor.callLater(2, p.transport.loseConnection)

c = ClientCreator(reactor, Greeter)
c.connectTCP("localhost", 8080).addCallback(gotProtocol)
reactor.run()
##c = ClientCreator(reactor, WelcomeMessage)
##c.connectTCP("localhost", 8080)
