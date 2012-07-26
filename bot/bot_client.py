
from test_client import Answer

ADMINISTRATORS = ('hannes', 'helena',)
COMMANDS = ('tell', 'shout', 'end', 'away', 'back', )

class Request:
    def __init__(self, dispatch, manage,):
        self.dispatch = dispatch
        self.manage = manage
        self.update()
        
    def receive(self, message):
        print 'got expected answer: >%s<' % message

    def update(self,):
        self.manage[self.expected] = self

    def purge(self,):
        for k,v in self.manage.items():
            if v == self:
                del self.manage[k]

class Welcome(Request):
    def __init__(self, dispatch, manage,):
        self.expected = "WELCOME TO"
        Request.__init__(self, dispatch, manage,)

    def receive(self, message):
        self.purge()
        self.dispatch.login()

class Login(Request):
    def __init__(self, dispatch, manage, user):
        self.expected = Answer('').complex_answer('login', [user,])
        Request.__init__(self, dispatch, manage,)

    def receive(self, message):
        expected_answer = self.expected.test(message)
        if expected_answer:
            self.purge()
            self.dispatch.query_status()
        return expected_answer

    def update(self,):
        self.manage['default'] = self

class Toggle(Request):
    def __init__(self, dispatch, manage,):
        self.expected = "The current settings are:"
        Request.__init__(self, dispatch, manage,)

    def receive(self, message):
        lines = message.splitlines()
        self.toggles = {}
        try:
            for t in lines[1:]:
                s = t.split()
                self.toggles[s[0]] = s[-1]
        except:
            raise RuntimeError('Toggle got unexpected data: >%s<' % message)
        self.dispatch.toggles = self.toggles
        if self.toggles['ready'] == 'NO':
            self.set_ready()
        self.purge()

    def set_ready(self,):
        self.dispatch.send_server('toggle ready')
        self.dispatch.toggles['ready'] = 'YES'

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
        self.send_server('toggle')

    def login(self,):
        login = Login(self, self.requests, self.user)
        self.send_server('login h h %s %s' % (self.user, self.password))

    def command(self, cmd):
        a = cmd.split()
        user = a[0]
        command = a[1]
        cmd_string = ' '.join(a[1:])
        if command in COMMANDS and user in ADMINISTRATORS:
            self.send_server(cmd_string)
        else:
            answer = "tell %s Ich bin ein bot. Red nicht so mit mir." % user
            self.send_server(answer)

    def parse(self, message):
        lines = message.splitlines()
        message_done = False
        if lines[0] in self.requests:
            # TODO: das funktioniert noch nicht.
            #       Versuch mal den bot auf 'away' zu setzen und dann zu starten
            #       Er bekommt die "away"-message als erste Zeile
            request = self.requests.pop(lines[0])
            request.receive(message)
            message_done = True
        elif 'default' in self.requests:
            request = self.requests['default']
            message_done = request.receive(message)
        if not message_done:
            if message.startswith('12 '):
                self.command(message[3:])
            else:
                print 'got from server: >%s<' % message
