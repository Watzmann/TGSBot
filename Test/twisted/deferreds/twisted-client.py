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
        s = raw_input('give me more >> ')
        return s

    def gotProtocol(self, p):
        print 'got protocol'
        self.protocol = p
        print 'start communication'
        self.input_loop()

    def send(self, msg):
        if msg.lower() in ('bye', 'exit', 'quit'):
            self.protocol.transport.loseConnection()
        else:
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
