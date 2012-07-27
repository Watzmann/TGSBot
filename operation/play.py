"""Commands about toggles, settings, etc."""

from operation.basics import Request, Response

class Join(Request):

    def __init__(self, dispatch, manage, opp, ML):
        self.expected = self.expected_answer(opp, ML)
        Request.__init__(self, dispatch, manage,)

    def expected_answer(self, opponent, ML):
        if ML is None:
            i_expect = "You are now playing with %s. " \
                       "Your running match was loaded." % opponent
        else:
            i_expect = "** You are now playing a %s " \
                       "point match with %s." % (ML, opponent)
        return i_expect

    def received(self, message):
        expected_answer = self.expected == message[0]
        if expected_answer:
            self.purge()
        return expected_answer

class Play(Request):

    class Answer(Response):

        def __init__(self, opp, ML):
            Response.__init__(self, '')
            self.complex_answer(self.join_answer, [opp, ML])

        def join_answer(self, expected, message):
            opponent = expected[0]
            ML = expected[1]
            if ML is None:
                i_expect = "You are now playing with %s. " \
                           "Your running match was loaded." % opponent
            else:
                i_expect = "** You are now playing a %s " \
                           "point match with %s." % (ML, opponent)
            return message[0] == i_expect

    def __init__(self, dispatch, manage, opp, ML):
        self.expected = self.Answer(opp, ML)
        Request.__init__(self, dispatch, manage,)

    def received(self, message):
        expected_answer = self.expected.test(message)
        if expected_answer:
            self.purge()
        return expected_answer

    def update(self,):
        self.manage['default'] = self
