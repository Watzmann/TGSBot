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
from operation.settings import Toggle, Set
from operation.invite import invite, Bots
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

class SetTest(Set):
    def set_dice_file(self,):
        self._dice = self.dispatch.get_gnubg().get_dice_filename()

    def _set_dice(self,):
        log.msg('SET sets dice to %s %s' % (self._dice, '>'*35),
                logLevel=VERBOSE)
        self.dispatch.send_server('set dice %s' % self._dice)

def invite_testbot(dispatch):
    def invite_one(bots):
        ML = dispatch.get_invite_ML()
        opp = dispatch.get_invite_player()
        log.msg("invite_one in .....testbot %s %s" % (ML, opp))
        if opp in bots and ML is not None:
            invite(dispatch, opp, ML)
        else:
            dispatch.relax_hook()

    log.msg("invite_testbot")
    bots = Bots(dispatch, dispatch.requests, invite_one)

class DispatchTest(Dispatch):
    auto_invite_hook = invite_testbot

    def _set_invite_MLs(self,):
        print "INVITES", self.get_gnubg().get_invites()
        for ml in self.get_gnubg().get_invites():
            yield ml

    def get_invite_player(self):
        return 'playerX'

    def get_invite_ML(self):
        try:
            ML = self.invite_MLs.next()
        except StopIteration:
            log.msg("Stop auto invite testbot!")
            self.autoinvite = False
            ML = None
        return ML

    def login_hook(self,):
        pfos = self.protocol.factory.options
        self.autoinvite = bool(self.get_gnubg().get_dice_filename())
        toggle = Toggle(self, self.requests)
        toggle.send_command('toggle')
        if self.autoinvite:
            self.nr_games = pfos.number_of_games
            self.invite_MLs = self._set_invite_MLs()
            settings = SetTest(self, self.requests)
            settings.set_dice_file()
        else:
            settings = Set(self, self.requests)
        settings.set_delay_value(pfos.delay)
        settings.send_command('set')
        self.relax_hook()

    def get_gnubg(self):
        return self.protocol.factory.gnubg.gnubg['gnubg']

def set_options(o):
    o.evaluate_mwc = False

def usage(progname):
    usg = """usage: %prog [<gid>] <test_game_data> <dice> <invitations>
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
    factory.dispatcher = DispatchTest(options.user, options.password,
                                      ka_lap=options.keep_alive,
                                      ignore_resume=options.ignore_resume)
    options.number_of_games = -1
    options.testgame = args[0]
    bridge = set_up_testgame(options.testgame)
    if not bridge is None:
        factory.gnubg = bridge
        bridge.set_bot(factory.dispatcher)
        standard_running = True
    else:
        print "Can't find %s." % options.testgame
        sys.exit(1)
    if standard_running:
        reactor.connectTCP(options.host, server_port, factory)
        reactor.run()
