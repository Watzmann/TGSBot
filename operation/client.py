"""Client supplies classes to run the client."""

from twisted.python import log
from operation.basics import Request
from operation.welcome import Welcome
from operation.welcome import Login
from operation.settings import Toggle, Set
from operation.play import Join
from operation.config import ADMINISTRATORS, COMMANDS

import sys

TRACE = 15
VERBOSE = 17

import logging
logging.addLevelName(TRACE, 'TRACE')
logging.addLevelName(VERBOSE, 'VERBOSE')
logging.basicConfig(level=logging.DEBUG,)
print 'client set logginglevel to', logging.getLevelName(logging.DEBUG)

class Dispatch:

    def __init__(self, protocol, user, password):
        self.protocol = protocol
        self.user = user
        self.password = password
        self.bot_uid = 0
        self.requests = {}
        welcome = Welcome(self, self.requests)

    def send_server(self, message):
        self.protocol.sendMessage(message)

    def set_bot_uid(self, uid):
        log.msg('My UID is %s' % uid, logLevel=logging.INFO)
        self.bot_uid = uid

    def set_boardstyle(self,):
        settings = Set(self, self.requests)
        settings.send_command('set')

    def query_status(self,):
        toggle = Toggle(self, self.requests)
        toggle.send_command('toggle')

    def join(self, opponent, ML):
        join = Join(self, self.requests, opponent, ML)
        join.send_command('join %s' % opponent)

    def login(self,):
        login = Login(self, self.requests, self.set_bot_uid)
        login.send_command('bot login h h %s %s' % (self.user, self.password))

    def command(self, cmd):
        a = cmd.split()
        user = a[0]
        command = a[1]
        cmd_string = ' '.join(a[1:])
        if command in COMMANDS and user in ADMINISTRATORS:
            self.send_server(cmd_string)
        else:
            answer = "tell %s I am a bot. Don't talk like that." % user
            self.send_server(answer)

    def parse(self, message):
        log.msg('#'*80, logLevel=logging.DEBUG)
        log.msg('MESSAGE %s' % message, logLevel=logging.DEBUG)
        lines = message.splitlines()
        while len(lines) > 0:
            first_line = lines[0]
            cmd_line = first_line.split()
            if len(cmd_line) == 0 or cmd_line[0] in ('5', '6'):
                del lines[0]
                continue
            log.msg('='*80, logLevel=logging.DEBUG)
            log.msg('COMMAND LINE %s' % cmd_line, logLevel=logging.DEBUG)
            log.msg('REQUEST %s' % self.requests, logLevel=logging.DEBUG)
            message_done = False

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
                        log.msg('joining a %s point match with %s' % (ML, opponent),
                                logLevel=logging.INFO)
                    else:
                        ML = None
                        log.msg('resuming a match with %s' % opponent,
                                logLevel=logging.INFO)
                    self.join(opponent, ML)
                if len(lines) > 0:
                    del lines[0]

        if len(lines) > 0:
            log.msg('got from server/lines left: >%s<' % '\n'.join(lines),
                                                logLevel=logging.DEBUG)
