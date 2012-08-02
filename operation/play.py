"""Commands about playing the match."""

import sys
from twisted.python import log
from operation.basics import Request, Response

TRACE = 15
VERBOSE = 17

import logging
logging.addLevelName(TRACE, 'TRACE')
logging.addLevelName(VERBOSE, 'VERBOSE')

sibs_path = '/var/develop/SIBS'
if not sibs_path in sys.path:
    sys.path.insert(0, sibs_path)

from board import Board

class Join(Request):

    def __init__(self, dispatch, manage, opp, ML):
        self.opponent = opp
        self.ML = ML
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
            Play(self.dispatch, self.manage, self.opponent,
                                     self.ML, resume=self.resume)
            del message[0]
        else:
            log.msg('JOIN applies NOT '+'-'*36, logLevel=VERBOSE)
        return expected_answer

class Play(Request):

##>
##bonehead and mehrdad start a 5 point match.
##>
##** Player sorrytigger has joined you for a 3 point match.
##Starting a new game with sorrytigger.
##You rolled 5, sorrytigger rolled 1
##It's your turn to move.
##    13 14 15 16 17 18       19 20 21 22 23 24
##   +------------------------------------------+ X: sorrytigger - score: 0
##   | O           X    |   |  X              O |
##   | O           X    |   |  X              O |
##   | O           X    |   |  X                |
##   | O                |   |  X                |
##   | O                |   |  X                |
##  v|                  |BAR|                   |    3-point match
##   | X                |   |  O                |
##   | X                |   |  O                |
##   | X           O    |   |  O                |
##   | X           O    |   |  O              X |
##   | X           O    |   |  O              X |
##   +------------------------------------------+ O: gutrune - score: 0
##    12 11 10  9  8  7        6  5  4  3  2  1
##
##   BAR: O-0 X-0   OFF: O-0 X-0   Cube: 1  You rolled 5 1.
##>
##sorrytigger kibitzes: Hi and good luck, greetings from Germany
##>
##thewronghands wins a 3 point match against once  3-1 .

    class Answer(Response):

        def __init__(self, opponent, ML, resume):
            Response.__init__(self, '')
            self.status = {}
            if resume:
                self.expected_answer = "Starting a new game with %s." % opponent
                self.complex_answer(self.resume_answer, [opponent,])
            else:
                self.expected_answer = "Starting a new game with %s." % opponent
                self.complex_answer(self.newgame_answer, [opponent, ML])

##        def resume_answer(self, expected, message):
##> turn: hannes.
##match length: 5
##points for helena: 0
##points for hannes: 0
## #board
##> Please move 2 pieces.

        def newgame_answer(self, expected, message):
            opponent = expected[0]
            ML = expected[1]
            try:
                if not message[1].startswith('You rolled'):
                    return False
                rollout = message[1]
                for msg in message[2:]:
                    if msg.startswith('You rolled'):
                        rollout = msg
                        continue
                a, b = rollout.split(',')
                dice_me = a.split(' ')[-1]
                dice_him = b.split(' ')[-1]
                self.status['dice'] = (dice_me, dice_him)
                if dice_me > dice_him:
                    idx = 1
                    for msg in message[2:]:
                        idx += 1
                        if msg.startswith('board'):
                            log.msg('ME starts', logLevel=VERBOSE)
                            log.msg('board: %s' % msg, logLevel=logging.DEBUG)
                            self.status['board'] = Board()
                            self.status['board'].load(msg)
                        if msg.startswith('Please move'):
                            log.msg('ME moves', logLevel=VERBOSE)
                            del message[:idx]
                            break
                elif dice_me < dice_him:
                    idx = 1
                    waitfor = '%s makes the first move.' % opponent
                    for msg in message[2:]:
                        idx += 1
                        if msg == waitfor:
                            log.msg('Opponent starts', logLevel=VERBOSE)
                            del message[:idx]
                            break
                # TODO: jetzt mussen folgende zwei zeilen 'umgehangt' werden
##                self.expected_answer = "Starting a new game with %s." % opponent
##                self.complex_answer(self.resume_answer, [opponent,])
            except:
                return False
            return True

    def __init__(self, dispatch, manage, opponent, ML, resume=False):
        self.expected = self.Answer(opponent, ML, resume)
        Request.__init__(self, dispatch, manage,)

    def received(self, message):
        log.msg('PLAY tests: %s' % message[0], logLevel=VERBOSE)
        expected_answer = self.expected.test(message)
        status = self.expected.status
        if expected_answer:
            log.msg('PLAY applies '+'+'*40, logLevel=VERBOSE)
            self.purge()
        else:
            log.msg('PLAY applies NOT '+'-'*36, logLevel=VERBOSE)
        return expected_answer

    def update(self,):
        self.manage[self.expected.expected_answer] = self
