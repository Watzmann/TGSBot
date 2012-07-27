
from operation.basics import Request
from operation.welcome import Welcome
from operation.welcome import Login
from operation.settings import Toggle, Set
from operation.play import Join
from operation.config import ADMINISTRATORS, COMMANDS

class Dispatch:

    def __init__(self, protocol, user, password):
        self.protocol = protocol
        self.user = user
        self.password = password
        self.requests = {}
        welcome = Welcome(self, self.requests)

    def send_server(self, message):
        self.protocol.sendMessage(message)

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
        login = Login(self, self.requests, self.user)
        login.send_command('login h h %s %s' % (self.user, self.password))

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
        lines = message.splitlines()
        cmd_line = lines[0].split()
        print 'COMMAND LINE', cmd_line
        print 'REQUEST', self.requests
        message_done = False
        checks = [0]
        for e,l in enumerate(lines[1:],1):
            if l in self.requests:
                checks.append(e)
        for c in checks:
            if lines[c] in self.requests:
                print 'ICH CHECKE -----------', lines[0]
                # TODO: das funktioniert noch nicht.
                #       Versuch mal den bot auf 'away' zu setzen und dann zu starten
                #       Er bekommt die "away"-message als erste Zeile
                request = self.requests.pop(lines[c])
                request.received(lines[c:])
                message_done = True
            elif 'default' in self.requests:
                print 'IN DEFAULT -----------'
                request = self.requests['default']
                message_done = request.received(lines[c:])
            if not message_done:
                if message.startswith('12 '):
                    #print 'command (1):', message
                    self.command(message[3:])
                elif len(cmd_line) > 3 and \
                     ' '.join(cmd_line[1:3]) == "wants to":
                    opponent = cmd_line[0]
                    if cmd_line[3] == 'play':
                        ML = int(cmd_line[5])
                        print 'joining a %s point match with %s' % (ML, opponent)
                    else:
                        ML = None
                        print 'resuming a match with %s' % opponent
                    self.join(opponent, ML)
                else:
                    print 'got from server: >%s<' % '\n'.join(lines[c:])
