#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) Copyright 2012 Andreas Hausmann
# This file is part of TGSBot.
# Permission to copy or use is limited. Please see LICENSE for information.
#
"""A twisted client as developing/testing tool for TGS.
Based on client/twisted-client1.py.
"""

from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.internet import reactor
from twisted.python import log
from operation.welcome import Welcome

TRACE = 15
VERBOSE = 17

import logging

class Com(Protocol):
    def __init__(self, factory):      # factory is neccessary in protocol,
        self.factory = factory        # since the dispatcher has to get hold
                                      # of factory properties

    def dataReceived(self, rawdata):
        data = rawdata.rstrip('\r\n')
        self.dispatch.parse(data)

    def sendMessage(self, msg):
        log.msg('>> %s' % msg, logLevel=logging.INFO)
        self.transport.write(msg + '\r\n')

    def connectionMade(self,):
        log.msg('connectionMade', logLevel=TRACE)
        self.dispatch = self.factory.dispatcher
        self.dispatch.protocol = self

    def dropConnection(self,):
        log.msg('dropConnection', logLevel=TRACE)
        self.transport.loseConnection()

class ComClientFactory(ReconnectingClientFactory):
    def reset_protocol_for_login(self,):
        dispatch = self.dispatcher
        dispatch.requests = {}
        Welcome(dispatch, dispatch.requests)

    def startedConnecting(self, connector):
        log.msg('Started to connect to tgs.', logLevel=TRACE)

    def buildProtocol(self, addr):
        log.msg('Connected to %s:%s.' % (self.options.host, self.options.port),
                                                                logLevel=TRACE)
        log.msg('Resetting reconnection delay.', logLevel=VERBOSE)
        self.resetDelay()
        return Com(self)

    def clientConnectionLost(self, connector, reason):
        log.msg('Lost connection. Reason: %s' % reason, logLevel=logging.INFO)
        if getattr(self, 'restart', True):
            self.reset_protocol_for_login()
            ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
        else:
            log.msg('Done - no restart', logLevel=logging.INFO)
            reactor.callWhenRunning(reactor.stop)

    def clientConnectionFailed(self, connector, reason):
        log.msg('Connection failed. Reason: %s' % reason, logLevel=logging.INFO)
        if getattr(self, 'restart', True):
            self.reset_protocol_for_login()
            ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
        else:
            log.msg('Done - no restart', logLevel=logging.INFO)
            reactor.callWhenRunning(reactor.stop)

    def stop(self,):
        self.restart = False
