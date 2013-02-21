#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) Copyright 2012 Andreas Hausmann
# This file is part of TGSBot.
# Permission to copy or use is limited. Please see LICENSE for information.
#
"""A twisted client that serves as playing bot for TGS.
  Based on client/twisted-client1.py.

  Example:
    ./tgsBot.py -P8081 -u tigerI |& tee /var/log/TGS/bot/tigerI.py.log
"""

from twisted.internet import reactor, defer
from twisted.python import log
import sys
from optparse import OptionParser

from operation.client import Dispatch
from client.gnubgClient import set_up_gnubg, GNUBG
from client.tgsClient import Com, ComClientFactory

TRACE = 15
VERBOSE = 17

import logging
logging.addLevelName(TRACE, 'TRACE')
logging.addLevelName(VERBOSE, 'VERBOSE')

NICK = 'test_bot_I'
KEEP_ALIVE = 300.

def start_logging(nick):
    log.startLogging(open('/var/log/TGS/bot/%s.log' % nick, 'a'))
    observer = log.PythonLoggingObserver()
    observer.start()

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
    parser.add_option("-k", "--keep-alive", default=KEEP_ALIVE,
                  action="store", dest="keep_alive", type="float",
                  help="keep alive lap in seconds. (%s)" % KEEP_ALIVE)
    parser.add_option("-s", "--strength", default='supremo',
                  action="store", dest="strength",
                  help="bots strength. (supremo)")
    parser.add_option("-d", "--delay", default='0.3',
                  action="store", dest="delay",
                  help="delay setting. (0.3)")
    parser.add_option("-I", "--auto-invite", default=False,
                  action="store_true", dest="auto_invite",
                  help="auto-invite other bots. (False)")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()

    start_logging(options.user)
    factory = ComClientFactory()
    factory.options = options
    server_port = int(options.port)
    factory.dispatcher = Dispatch(options.user, options.password,
                                    options.strength, options.keep_alive)
    # connect to a running gnubg instance
    gnubg = set_up_gnubg('localhost', port=GNUBG)
    if not gnubg is None:    # TODO: react to missing gnubg (now start one)
        factory.gnubg = gnubg
        reactor.connectTCP(options.host, server_port, factory)
        reactor.run()
    else:
        print "Can't find gnubg"
