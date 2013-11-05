
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
            ret += not msgs[3].startswith('3')
            ret += not msgs[4].startswith('+--')
            m = 5
            while not msgs[m].startswith('+--'):
                m += 1
            ret += not msgs[m+1].startswith('4')
            m = m + 3
            while msgs[m].startswith('5 '):
                m += 1
            ret += not msgs[m].startswith('6')
        except:
            return False
        return not ret

    def trivial(self, expected, message):
        return expected == message

    def test(self, message):
        check, expected = self.answer
        return check(expected, message)

