# -*- coding: utf-8 -*-
#
# (c) Copyright 2012 Andreas Hausmann
# This file is part of TGSBot.
# Permission to copy or use is limited. Please see LICENSE for information.
#
"""Client supplies classes to run the admin client."""

from os import getcwd
from twisted.internet import reactor
from twisted.python import log
from operation.basics import Request
from operation.welcome import Welcome
from operation.welcome import Login
from operation.settings import Toggle, Set
from operation.invite import invite, join
from operation.config import ADMINISTRATORS, COMMANDS, MAX_MATCHLEN

import sys

NOISY = 7
TRACE = 15
VERBOSE = 17

import logging
logging.addLevelName(TRACE, 'NOISY')
logging.addLevelName(TRACE, 'TRACE')
logging.addLevelName(VERBOSE, 'VERBOSE')
level = NOISY
if getcwd().startswith('/var/opt/tgs'):
    level = max(level, logging.DEBUG)
logging.basicConfig(level=level,)
print 'client set logginglevel to', logging.getLevelName(level)

class Dispatch:

    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.requests = {}
        welcome = Welcome(self, self.requests)

    def send_server(self, message):
        self.protocol.sendMessage(message)

    def set_bot_uid(self, uid):
        log.msg('My UID is %s' % uid, logLevel=logging.INFO)
        self.bot_uid = uid

    def login_hook(self,):
        log.msg("In login_hook", logLevel=TRACE)
        if hasattr(self.protocol.factory, 'command_file'):
            #log.msg("Processing command file", logLevel=TRACE)
            with self.protocol.factory.command_file as f:
                for line in f:
                    cmd = line.rstrip('\n')
                    #log.msg(cmd, logLevel=logging.INFO)
                    self.send_server(cmd)
        reactor.callLater(2., reactor.callWhenRunning, reactor.stop)

    def login(self,):
        login = Login(self, self.requests, self.set_bot_uid, "hello sir :)")
        login.send_command(self.user)
        reactor.callLater(2.0, login.send_command, self.password)

    def command(self, cmd):
        a = cmd.split()
        user = a[0]
        command = a[1]
        cmd_string = ' '.join(a[1:])
        if command in COMMANDS and user in ADMINISTRATORS:
            if command in ('end',):
                self.protocol.factory.stop()
            elif command == 'invite' and a[3] <= MAX_MATCHLEN:
                invite(a[2], a[3])
            else:
                self.send_server(cmd_string)

    def parse(self, message):
        log.msg('#'*80, logLevel=NOISY)
        log.msg('MESSAGE %s' % message, logLevel=NOISY)
        lines = message.splitlines()
        while len(lines) > 0:
            first_line = lines[0]
            cmd_line = first_line.split()
            if len(cmd_line) == 0 or cmd_line[0] in \
                                        ('3', '4', '5', '6', '7', '8', '13'):
                del lines[0]
                continue
            log.msg('='*80, logLevel=logging.DEBUG)
            log.msg('COMMAND LINE %s' % cmd_line, logLevel=logging.DEBUG)
            log.msg('REQUEST %s' % self.requests, logLevel=logging.DEBUG)
            message_done = False

            if first_line.startswith('** '):
                # TODO hier gehört noch ein Abfangjäger für reichlich normale
                #      Meldungen rein (** Player helena has left the game...)
                log.msg('from server: %s' % first_line, logLevel=logging.WARNING)

            for r in self.requests:
                if first_line.startswith(r):
                    log.msg('ICH CHECKE ----------- %s' % first_line, logLevel=TRACE)
                    # TODO: das funktioniert noch nicht.
                    #       Versuch mal den bot auf 'away' zu setzen und dann zu starten
                    #       Er bekommt die "away"-message als erste Zeile
                    request = self.requests.pop(r)
                    log.msg('1 ################# %s' % len(lines), logLevel=logging.DEBUG)
                    message_done = request.received(lines)
                    log.msg('2 ################# %s (%s)' % (len(lines),message_done), logLevel=logging.DEBUG)
                    break
            if not message_done and 'default' in self.requests:
                # TODO: schauen, ob man das noch braucht
                log.msg('IN DEFAULT ----------- %s' % first_line, logLevel=TRACE)
                request = self.requests['default']
                log.msg('3 ################# %s' % len(lines), logLevel=logging.DEBUG)
                message_done = request.received(lines)
                log.msg('4 ################# %s (%s)' % (len(lines),message_done), logLevel=logging.DEBUG)

            if not message_done:
                if first_line.startswith('12 '):
                    self.command(first_line[3:])
                elif len(cmd_line) > 3 and \
                                        ' '.join(cmd_line[1:3]) == "wants to":
                    opponent = cmd_line[0]
                    if cmd_line[3] == 'play':
                        ML = int(cmd_line[5])
                        if ML > 0 and ML <= MAX_MATCHLEN:
                            join(opponent, ML)
                            log.msg('joining a %d point match with %s' % \
                                        (ML, opponent), logLevel=logging.INFO)
                        else:
                            msg = "tell %s I do not as yet play matches " \
                                  "greater than ML %d or unlimited. Sorry." % \
                                                    (opponent, MAX_MATCHLEN)
                            self.send_server(msg)
                            log.msg('turning down a %d point match with %s' % \
                                        (ML, opponent), logLevel=logging.INFO)
                    else:
                        ML = None
                        log.msg('resuming a match with %s' % opponent,
                                logLevel=logging.INFO)
                        join(opponent, ML)
                if len(lines) > 0:
                    del lines[0]

        if len(lines) > 0:
            log.msg('got from server/lines left: >%s<' % '\n'.join(lines),
                                                logLevel=logging.DEBUG)
