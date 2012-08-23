#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Ein Twisted-Client als Entwicklungs-Hilfe/Tool for SIBS.
Basiert auf client/twisted-client1.py. Das Reconnecting-Zeugs ist raus.
"""

from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.internet import reactor, defer
from twisted.python import log
import sys
import random
from optparse import OptionParser

from operation.client import Dispatch
from client.gnubg_client import set_up_gnubg

TRACE = 15
VERBOSE = 17

import logging
logging.addLevelName(TRACE, 'TRACE')
logging.addLevelName(VERBOSE, 'VERBOSE')

NICK = 'test_bot_I'

def start_logging(nick):
    log.startLogging(open('/var/log/SIBS/bot/%s.log' % nick, 'a'))
    observer = log.PythonLoggingObserver()
    observer.start()

class Com(Protocol):
    def __init__(self, options, factory):
        self.options = options
        self.factory = factory

    def dataReceived(self, rawdata):
        data = rawdata.rstrip('\r\n')
        self.dispatch.parse(data)

    def sendMessage(self, msg):
        log.msg('>> %s' % msg, logLevel=logging.INFO)
        self.transport.write(msg + '\r\n')

    def connectionMade(self,):
        log.msg('connectionMade', logLevel=TRACE)
        user = self.options.user
        password = self.options.password
        self.dispatch = Dispatch(self, user, password)

    def dropConnection(self,):
        log.msg('dropConnection', logLevel=TRACE)
        self.transport.loseConnection()

class ComClientFactory(ReconnectingClientFactory):
    def startedConnecting(self, connector):
        log.msg('Started to connect.', logLevel=TRACE)

    def buildProtocol(self, addr):
        log.msg('Connected to %s:%s.' % (options.host, options.port), logLevel=TRACE)
        log.msg('Resetting reconnection delay.', logLevel=VERBOSE)
        self.resetDelay()
        return Com(self.options, self)

    def clientConnectionLost(self, connector, reason):
        log.msg('Lost connection. Reason: %s' % reason, logLevel=logging.INFO)
        if getattr(self, 'restart', True):
            ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
        else:
            log.msg('Done - no restart', logLevel=logging.INFO)
            reactor.callWhenRunning(reactor.stop)

    def clientConnectionFailed(self, connector, reason):
        log.msg('Connection failed. Reason: %s' % reason, logLevel=logging.INFO)
        if getattr(self, 'restart', True):
            ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
        else:
            log.msg('Done - no restart', logLevel=logging.INFO)
            reactor.callWhenRunning(reactor.stop)

    def stop(self,):
        self.restart = False

def usage(progname):
    usg = """usage: %prog [<gid>]
  %prog """ + __doc__
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print full entries to stdout")
    parser.add_option("-u", "--user", default=NICK,
                  action="store", dest="user",
                  help="user name (nick).")
    parser.add_option("-p", "--password", default='hallo',
                  action="store", dest="password",
                  help="users password.")
    parser.add_option("-H", "--host", default='localhost',
                  action="store", dest="host",
                  help="host. (localhost)")
    parser.add_option("-P", "--port", default='8081',
                  action="store", dest="port",
                  help="server port. (8081)")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()

    start_logging(options.user)
    factory = ComClientFactory()
    factory.options = options
    # connect to a running gnubg instance
    # TODO: react to missing gnubg (either start one, or fail)
    server_port = int(options.port)
    factory.gnubg = set_up_gnubg('localhost', port=8083)
    reactor.connectTCP(options.host, server_port, factory)
    reactor.run()
