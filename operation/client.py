# -*- coding: utf-8 -*-
#
# (c) Copyright 2012 Andreas Hausmann
# This file is part of TGSBot.
# Permission to copy or use is limited. Please see LICENSE for information.
#
"""Client supplies classes to run the client."""

from os import getcwd
from twisted.internet import reactor
from twisted.python import log
from operation.basics import Request
from operation.welcome import Welcome
from operation.welcome import Login
from operation.settings import Toggle, Set, GnubgSettings
from operation.invite import invite, join, invite_bots
from operation.config import ADMINISTRATORS, COMMANDS, MAX_MATCHLEN

import sys

NOISY = 7
TRACE = 15
VERBOSE = 17

import logging
logging.addLevelName(TRACE, 'NOISY')
logging.addLevelName(TRACE, 'TRACE')
logging.addLevelName(VERBOSE, 'VERBOSE')
level = logging.INFO    # NOISY
if getcwd().startswith('/var/opt/tgs'):
    level = max(level, logging.DEBUG)
logging.basicConfig(level=level,)
print 'client set logginglevel to', logging.getLevelName(level)

class ResignHandler:

    levels = dict(zip(('n', 'g', 'b'), (1, 2, 3)))

    def __init__(self,):
        self.reset()

    def reset(self,):
        self.level = 1

    def possible(self, resign):
        log.msg('in resign considering: %s' % resign, logLevel=TRACE)
        proposed_level = self.levels[resign.split()[-1]]
        log.msg('resign possible?? level: %d   proposed: %d' % \
                        (self.level, proposed_level), logLevel=logging.DEBUG)
        if proposed_level < self.level:
            return ''
        else:
            self.level = proposed_level
            return resign

    def rejected(self,):
        self.level = min(4, self.level + 1)

class Dispatch:

    def __init__(self, user, password, strength='supremo', ka_lap=300.):
        self.user = user
        self.password = password
        self.strength = strength
        self.bot_uid = 0
        self.requests = {}
        self.told_opponent = {}
        self.user_commands = {'info': self.user_info,
                              }
        self.keepalive_lap = ka_lap
        self.keep_alive = reactor.callLater(ka_lap, self.send_keepalive)
        self.resigns = ResignHandler()
        welcome = Welcome(self, self.requests)
    # TODO: wrong way to start login sequence
    #       The way it works now it won't login again when reconnecting!

    def send_keepalive(self,):
        self.send_server('ka')

    def reset_keepalive(self,):
        if self.keep_alive.active():
            self.keep_alive.reset(self.keepalive_lap)
        else:
            self.keep_alive = reactor.callLater(self.keepalive_lap,
                                                        self.send_keepalive)

    def send_server(self, message):
        self.protocol.sendMessage(message)
        self.reset_keepalive()

    def set_bot_uid(self, uid):
        log.msg('My UID is %s' % uid, logLevel=logging.INFO)
        self.bot_uid = uid
        self.protocol.factory.gnubg.gnubg.set_uid_and_strength(uid, self.strength)

    def delete_told_opponent(self, user):
        if user in self.told_opponent:
            del self.told_opponent[user]

    def login_hook(self,):
        toggle = Toggle(self, self.requests)
        toggle.send_command('toggle')
        settings = Set(self, self.requests)
        settings.set_delay_value(self.protocol.factory.options.delay)
        settings.send_command('set')
        self.relax_hook()

    def relax_hook(self,):
        if hasattr(self, 'saved'):
            self.saved.purge()
            del self.saved
        if self.protocol.factory.options.auto_invite:
            self.invitation = reactor.callLater(5., invite_bots, self)

    def login(self,):
        login = Login(self, self.requests, self.set_bot_uid)
        login.send_command('bot login h h %s %s' % (self.user, self.password))

    def user_info(self, user):
        def return_info(infos):
            info = "I am an expert playing bot"
            self.send_server("tell %s %s" % (user, info))
# TODO
        gnubg = self.protocol.factory.gnubg.gnubg
        GnubgSettings('get_player', [], gnubg, return_info)

    def command(self, cmd):
        a = cmd.split()
        user = a[0]
        command = a[1]
        cmd_string = ' '.join(a[1:])
        if command in COMMANDS and user in ADMINISTRATORS:
            log.msg('%s tells me to: %s' % \
                                    (user, cmd_string), logLevel=logging.INFO)
            if command in ('end',):
                self.protocol.factory.stop()
                self.send_server('wave')
                self.send_server('wave')
            elif command == 'invite':
                if len(a) < 4:
                    invite(self, a[2], None)
                elif a[3] != 'unlimited' and int(a[3]) <= MAX_MATCHLEN:
                    invite(self, a[2], a[3])
                else:
                    log.msg('turning down a %s point invitation with %s' % \
                                            (a[3], a[2]), logLevel=logging.INFO)
            else:
                self.send_server(cmd_string)
        else:
            log.msg('%s says: %s' % (user, cmd_string), logLevel=logging.INFO)
            if command in ('info',):
                self.user_commands[command](user)
            else:
                msg = "tell %s I am a bot. I don't know how to talk, yet. Sorry."
                if not user in self.told_opponent:
                    self.told_opponent[user] = True
                    self.send_server(msg % user)
                    reactor.callLater(300., self.delete_told_opponent, user)

    def parse(self, message):
        log.msg('#'*80, logLevel=NOISY)
        log.msg('MESSAGE %s' % message, logLevel=NOISY)
        self.reset_keepalive()
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
                        ML = cmd_line[5]
                        if ML == 'unlimited':
                            join(self, opponent, ML, type_of_invitation=1)
                            log.msg('joining an unlimited match with %s' % \
                                            opponent, logLevel=logging.INFO)
                        elif int(ML) > 0 and int(ML) <= MAX_MATCHLEN:
                            join(self, opponent, ML)
                            log.msg('joining a %s point match with %s' % \
                                        (ML, opponent), logLevel=logging.INFO)
                        else:
                            msg = "tell %s I do not play matches greater " \
                                  "than ML %d. Sorry." % \
                                                    (opponent, MAX_MATCHLEN)
                            self.send_server(msg)
                            log.msg('turning down a %s point match with %s' % \
                                        (ML, opponent), logLevel=logging.INFO)
                    else:
                        ML = None
                        log.msg('resuming a match with %s' % opponent,
                                logLevel=logging.INFO)
                        join(self, opponent, ML)
                if len(lines) > 0: # TODO: Scheisse, hier schmeiss ich unverarbeitetes weg?? :((
                    log.msg('deleting command line: >%s<' % lines[0], logLevel=logging.DEBUG)
                    del lines[0]

        if len(lines) > 0:
            log.msg('got from server/lines left: >%s<' % '\n'.join(lines),
                                                logLevel=logging.DEBUG)
