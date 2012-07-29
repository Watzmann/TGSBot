"""Commands about toggles, settings, etc."""

from twisted.python import log
from operation.basics import Request, Response

TRACE = 15
VERBOSE = 17

import logging
logging.addLevelName(TRACE, 'TRACE')
logging.addLevelName(VERBOSE, 'VERBOSE')

class Join(Request):

    def __init__(self, dispatch, manage, opp, ML):
        self.expected = self.expected_answer(opp, ML)
        Request.__init__(self, dispatch, manage,)

    def expected_answer(self, opponent, ML):
        if ML is None:
            i_expect = "You are now playing with %s. " \
                       "Your running match was loaded." % opponent
            self.resume = True
        else:
            i_expect = "** You are now playing a %s " \
                       "point match with %s." % (ML, opponent)
            self.resume = False
        return i_expect

    def received(self, message):
        log.msg('JOIN tests: %s' % message[0], logLevel=VERBOSE)
        expected_answer = self.expected == message[0]
        if expected_answer:
            log.msg('JOIN applies '+'+'*40, logLevel=VERBOSE)
            self.purge()
            Play(self.dispatch, self.manage, resume=self.resume)
        else:
            log.msg('JOIN applies NOT '+'-'*36, logLevel=VERBOSE)
        return expected_answer

class Play(Request):

    class Answer(Response):

        def __init__(self,):
            Response.__init__(self, '')
            self.complex_answer(self.play_answer, [2, 1])

## starting a new game
## -----------------
##Starting a new game with helena.
##> You rolled 3, helena rolled 1
##> It's your turn to move.
## #board
##> Please move 2 pieces.


## resuming a game
## -----------------
##You are now playing with helena. Your running match was loaded.
##> turn: hannes.
##match length: 5
##points for helena: 0
##points for hannes: 0
## #board
##> Please move 2 pieces.


        def play_answer(self, expected, message):
            opponent = expected[0]
            ML = expected[1]
            if ML is None:
                i_expect = "You are now playing with %s. " \
                           "Your running match was loaded." % opponent
            else:
                i_expect = "** You are now playing a %s " \
                           "point match with %s." % (ML, opponent)
            return message[0] == i_expect

    def __init__(self, dispatch, manage, resume=False):
        self.expected = self.Answer()
        Request.__init__(self, dispatch, manage,)

    def received(self, message):
        log.msg('PLAY tests: %s' % message[0], logLevel=VERBOSE)
        expected_answer = self.expected.test(message)
        if expected_answer:
            log.msg('PLAY applies '+'+'*40, logLevel=VERBOSE)
            self.purge()
        else:
            log.msg('PLAY applies NOT '+'-'*36, logLevel=VERBOSE)
        return expected_answer

    def update(self,):
        self.manage['default'] = self
