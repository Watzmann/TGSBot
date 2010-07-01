#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Das Tutorial twisted-core.pdf Kapitel 2.6.
Growing example
"""

from twisted.internet import protocol, reactor
from twisted.protocols import basic

class FingerProtocol(basic.LineReceiver):
    def lineReceived(self, user):
        self.transport.write(self.factory.getUser(user)+"\r\n")
        self.transport.loseConnection()

class FingerFactory(protocol.ServerFactory):
    protocol = FingerProtocol

    def getUser(self, user):
        return "No such user"

reactor.listenTCP(1079, FingerFactory())
reactor.run()
