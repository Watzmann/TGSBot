
f = open('/var/develop/SIBS/resources/extro')
BYE = f.read()
f.close()
#BYE += "     As no one seems to type 'about' - here is what it says:\n\n"
f = open('/var/develop/SIBS/resources/about')
BYE += f.read()
f.close()

class Answer:

    def __init__(self, answer):
        self.answer = (self.trivial, answer)

    def complex_answer(self, key, expected):
        answers = {'login': self.login_answer,
                   }
        self.answer = (answers[key], expected)
        return self

    def login_answer(self, expected, message):
        user = expected[0]
        msgs = message.split('\n')
        try:
            ret = not msgs[1].startswith('1 %s' % user)
            ret += not msgs[2].startswith('2 %s' % user)
            ret += not msgs[3].startswith('TGS')
            ret += not msgs[4].startswith('3')
            ret += not msgs[5].startswith('+--')
            m = 6
            while not msgs[m].startswith('+--'):
                m += 1
            ret += not msgs[m+1].startswith('4')
            m = m + 2
            while not msgs[m].startswith('5 '):
                m += 1
            ret += not msgs[m+2].startswith('6')
            ret += not msgs[m+4].startswith('5 %s' % user)
            ret += not msgs[m+5].startswith('6')
            #print '****** %s ****' % ret, msgs[m+5], '#'
        except:
            return False
        return not ret

    def trivial(self, expected, message):
        return expected == message

    def test(self, message):
        check, expected = self.answer
        return check(expected, message)

class Dispatch:

    def __init__(self, protocol, user, password):
        self.protocol = protocol
        self.user = user
        self.password = password

    def login(self,):
        self.protocol.sendMessage('login h h %s %s' % (self.user, self.password))
        self.expected_answer = Answer('').complex_answer('login', [self.user,])
        return True

    def bye(self,):
        self.protocol.sendMessage('bye')
        self.expected_answer = Answer(BYE.rstrip('\n'))
        return True

    def simple_command(self, cmd_string, expected, wait):
        self.protocol.sendMessage(cmd_string)
        self.expected_answer = Answer(expected)
        return wait

    def parse(self, message):
        waiting_for_answer = False
        if message.startswith('WELCOME'):
            if message.endswith('login: '):
                waiting_for_answer = self.login()
            else:
                print 'message ends strangely:', message[-20:]
        else:
            print 'got from server:', message
        return waiting_for_answer
