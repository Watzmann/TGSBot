
from test_client import Answer

class Dispatch:

    def __init__(self, protocol, user, password):
        self.protocol = protocol
        self.user = user
        self.password = password
        self.waiting_for_answer = False
        self.parse = self.parse_standard

    def login(self,):
        self.protocol.sendMessage('login h h %s %s' % (self.user, self.password))
        self.expected_answer = Answer('').complex_answer('login', [self.user,])
        return True

    def query_status(self,):
        self.parse = self.eval_toggle
        self.protocol.sendMessage('toggle')
    # ich weiss gar nicht, wann ich diesen befehl absetzen kann und wie ich
    # die korrekte Antwort rausfische
    # Alles ist asynchron: wie setze ich request und antwort sauber zusammen?
    
##        self.expected_answer = Answer('').complex_answer('login', [self.user,])
##        return True

    def eval_toggle(self,):
        self.parse = self.restore_parse

    def bye(self,):
        self.protocol.sendMessage('bye')

    def command(self, cmd):
        a = cmd.split()
        user = a[0]
        command = a[1]
        cmd_string = ' '.join(a[1:])
        if command in ('tell', 'shout', 'end', '', ):
            self.protocol.sendMessage(cmd_string)
        else:
            answer = "tell %s Ich bin ein bot. Red nicht so mit mir." % user
            self.protocol.sendMessage(answer)

    def parse_standard(self, message):
        if self.waiting_for_answer:
            if self.expected_answer.test(message):
                self.waiting_for_answer = False
            else:
                raise RuntimeError('Got unexpected data: %s##' % message)
        else:
            if message.startswith('WELCOME'):
                self.waiting_for_answer = self.login()
            elif message.startswith('12 '):
                self.command(message[3:])
            else:
                print 'got from server: >%s<' % message
