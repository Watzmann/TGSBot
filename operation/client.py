
from operation.basics import Request
from operation.welcome import Welcome
from operation.welcome import Login
from operation.settings import Toggle, Join
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

    def query_status(self,):
        toggle = Toggle(self, self.requests)
        toggle.send_command('toggle')

    def join(self, opponent):
        join = Join(self, self.requests)
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
        personal = lines[0].split()
        print 'PERSONAL', personal
        message_done = False
        if lines[0] in self.requests:
            print 'ICH CHECKE -----------', lines[0]
            # TODO: das funktioniert noch nicht.
            #       Versuch mal den bot auf 'away' zu setzen und dann zu starten
            #       Er bekommt die "away"-message als erste Zeile
            request = self.requests.pop(lines[0])
            request.receive(message)
            message_done = True
        elif 'default' in self.requests:
            print 'IN DEFAULT -----------'
            request = self.requests['default']
            message_done = request.receive(message)
        if not message_done:
            if message.startswith('12 '):
                #print 'command (1):', message
                self.command(message[3:])
            elif len(personal) > 3 and \
                 ' '.join(personal[1:3]) == "wants to":
                opponent = personal[0]
                if personal[3] == 'play':
                    ML = int(personal[5])
                else:
                    ML = None
                print 'joining a %s point match with %s' % (ML, opponent)
                self.join(opponent)
            else:
                print 'got from server: >%s<' % message
