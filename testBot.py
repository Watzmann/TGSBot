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

from tgsBot import get_parser
from operation.client import Dispatch
from client.gnubgClient import set_up_testgame
from client.tgsClient import ComClientFactory

TRACE = 15
VERBOSE = 17

import logging
logging.addLevelName(TRACE, 'TRACE')
logging.addLevelName(VERBOSE, 'VERBOSE')

NICK = 'test_bot_I'
KEEP_ALIVE = 300.

def start_logging(nick):
    log.startLogging(open('/var/log/TGS/bots/%s.log' % nick, 'a'))
    observer = log.PythonLoggingObserver()
    observer.start()

def set_options(o):
    o.evaluate_mwc = False

def usage(progname):
    usg = """usage: %prog [<gid>]
  %prog """ + __doc__
    parser = get_parser(usg)
    return parser, usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    set_options(options)

    start_logging(options.user)
    factory = ComClientFactory()
    factory.options = options
    server_port = int(options.port)
    factory.dispatcher = Dispatch(options.user, options.password,
                    ka_lap=options.keep_alive)
    # set up a testgame instance
    testgame = "test_game.data"
    bridge = set_up_testgame(testgame)
    if not bridge is None:
        factory.gnubg = bridge
        bridge.set_bot(factory.dispatcher)
        standard_running = True
    else:
        print "Can't find %s." % testgame
        sys.exit(1)
    if standard_running:
        reactor.connectTCP(options.host, server_port, factory)
        reactor.run()
