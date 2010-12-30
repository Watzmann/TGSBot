#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Ein Twisted-Client zu Testzwecken zum Thema 'twisted'.
Siehe twisted-core.pdf, Kap. 2.2.
"""

from twisted.internet import reactor, defer, threads
from twisted.internet.protocol import Protocol, ClientCreator
from sys import stdout
import time

class Greeter(Protocol):
    def sendMessage(self, msg):
        print 'in sendMessage with', msg
        self.transport.write("MESSAGE %s\n" % msg)

    def connectionMade(self):
        print 'connection made'

    def connectionLost(self, reason):
        # Damit wird der reactor beendet; sonst würde das Ding endlos laufen
        # connectionLost ist der richtige Zeitpunkt; macht man es z.B. in
        # gotProtocol(), dann würden die 'callLater'-Aufrufe auch beendet, also
        # nicht ausgeführt werden.
        reactor.stop()

    def dataReceived(self, data):
        stdout.write(data)

class Communicator:
    def communicate(self,):  #p, d):
        """Do a bit of manual communication with the server. Quit with a keyword."""
##        while True:
        s = raw_input('give me more >> ')
        if s.lower() in ('bye', 'exit', 'quit'):
            self.protocol.transport.loseConnection()
        return s
##                break
##            else:
##                self.protocol.sendMessage(s)
##                d.callback(s)

##    def get_communicator(p):
##        d = defer.Deferred()
##        reactor.callLater(2, communicate, p, d)
##        return d

    def gotProtocol(self, p):
    ##    d = get_communicator(p) # communication with server is deferred
    ##    print 'defer', d
    ##    def onError(err):
    ##        return 'Internal error in communication'
    ##    d.addErrback(onError)
    ##    
    ##    def writeResponse(message):
    ##        print 'sending', message
    ##        p.sendMessage(message)
    ##    d.addCallback(writeResponse)
    ##
    ##    p.sendMessage("Hello")
    ##    reactor.callLater(1, p.sendMessage, "This is sent in a second")
        print 'got protocol'
        self.protocol = p
        print 'start communication'
##        com.communicate()
        self.input_loop()

    def send(self, msg):
        self.protocol.sendMessage(msg)
        self.input_loop()

    def input_loop(self,):
        d = threads.deferToThread(self.communicate)
        d.addCallback(self.send)
    
com = Communicator()
print 'com made'
c = ClientCreator(reactor, Greeter)
print 'creator made'
c.connectTCP("localhost", 8080).addCallback(com.gotProtocol)
print 'connected'
reactor.run()
# hier muss echt nix mehr stehen; wir sind doch in der main loop vom reactor!
