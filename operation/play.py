# -*- coding: utf-8 -*-
"""Commands about playing the match."""

import sys
import time
from twisted.python import log
from twisted.internet import defer
from operation.basics import Request, Response

TRACE = 15
VERBOSE = 17

import logging
logging.addLevelName(TRACE, 'TRACE')
logging.addLevelName(VERBOSE, 'VERBOSE')

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

        def __init__(self, gnubg, opponent, ML, resume):
            Response.__init__(self, '')
            self.gnubg = gnubg
            self.status = {}
            if resume:
                self.expected_answer = "points for %s:" % opponent
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

## !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
##  Ich gebe den Bots n Flag mit (PlayBot).
##  Damit können sie Infos abfragen (besonderer Commando-Satz).
##  Dann wird ihnen vom Server signalisiert, dass von ihnen eine
##    Aktion erwartet wird (Trigger). Mit Commandos holen sie die
##    benötigte Info und können die Aktion ausführen.

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
                        if msg.startswith('match_id'):
                            log.msg('ME starts', logLevel=VERBOSE)
                            m,p = msg.split()[1].split(':')
                            self.status['match_id'] = m
                            self.status['position_id'] = p
                            match_id = '%s:%s' % (m, p)
                            log.msg('match_id: %s' % match_id, logLevel=logging.DEBUG)
                            # rausfinden, ob ich dran
                            # deferred Frage abschicken; wenn antwort, sofort senden
                            self.oracle = self.gnubg.gnubg.ask_gnubg('bestMove: %s' % match_id)
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
                raise
                return False
            return True

        def resume_answer(self, expected, message):
            opponent = expected[0]
            return True

        def get_oracle(self,):
            return getattr(self, 'oracle', None)

    def __init__(self, dispatch, manage, opponent, ML, resume=False):
        self.gnubg = dispatch.protocol.factory.gnubg
        self.opponent = opponent
        self.ML = ML
        self.expected = self.Answer(self.gnubg, opponent, ML, resume)
        self.expected.send_move = self.send_move
        self.label = 'PLAY'
        self.sent_request = time.time()
        Request.__init__(self, dispatch, manage,)

    def send_move(self, move):
        log.msg('got move: %s' % move, logLevel=logging.DEBUG)
        # TODO: hier fehlt komplett die Behandlung, welche Richtung der Bot spielt
        #       er wird bei den Lasttests auch mal selber einladen!!
        mv = ' '.join(['m',] + [str(25-int(m)) for m in move.strip('()').split(',')])
        #self.send_command(mv)

    def received(self, message):
        log.msg(self.msg_tests % message[0], logLevel=VERBOSE)
        expected_answer = self.expected.test(message)
        status = self.expected.status   # TODO: brauch ich das noch??
        if expected_answer:
            oracle = self.expected.get_oracle()
            log.msg('does oracle work?? %s' % oracle, logLevel=logging.DEBUG)
            if not oracle is None:
                oracle.addCallback(self.send_move)
            log.msg(self.msg_applies + '+'*40, logLevel=VERBOSE)
            time_used = time.time() - self.sent_request
            log.msg(self.msg_waited % time_used, logLevel=logging.INFO)
            self.purge()
            Turn(self.dispatch, self.manage,)
            del message[0]
        else:
            log.msg('PLAY applies NOT '+'-'*36, logLevel=VERBOSE)
        return expected_answer

    def update(self,):
        self.manage[self.expected.expected_answer] = self

class Action:
    """Action objects can take one of six orders and then, if appropriate, ask
    gnubg for the proper action to take in this case.
"""
    def __init__(self, order, parameters, gnubg, callback):
        log.msg('create action with (%s - %s)' % (order, parameters),
                                                        logLevel=logging.DEBUG)
        self.gnubg = gnubg
        self.callback = callback
        {'double': self._double,    # state B - double or roll? resign?
         'move': self._move,        # state E - which move? resign?
         'take': self._take,        # state C - take the cube?
         'accept': self._accept,    # state J - accept the resign?
         'join': self._true,        # state G - return the neccessary 'join'
         'relax': self._relax,      # state G - be polite and return thanks
         }[order](parameters)

    def _double(self, parameters):
        self.oracle = self.gnubg.ask_gnubg('double: %s resign' % parameters[0])
        log.msg('got DOUBLE oracle: %s' % self.oracle, logLevel=logging.DEBUG)
        if not self.oracle is None:
            self.oracle.addCallback(self.callback)

    def _take(self, parameters):
        self.oracle = self.gnubg.ask_gnubg('take: %s' % parameters[0])
        log.msg('got TAKE oracle: %s' % self.oracle, logLevel=logging.DEBUG)
        if not self.oracle is None:
            self.oracle.addCallback(self.callback)

    def _move(self, parameters):
        self.oracle = self.gnubg.ask_gnubg('bestMove: %s %s resign' % \
                                            (parameters[0], parameters[1]))
        log.msg('got MOVE oracle: %s' % self.oracle, logLevel=logging.DEBUG)
        if not self.oracle is None:
            self.oracle.addCallback(self.callback)

    def _accept(self, parameters):
        self.oracle = defer.Deferred()
        self.oracle.addCallback(self.callback)
        self.oracle.callback(False)

    def _relax(self, parameters):
        self.oracle = defer.Deferred()
        self.oracle.addCallback(self.callback)
        log.msg('sending relax: %s' % parameters[1], logLevel=logging.DEBUG)
        self.oracle.callback(parameters[1] == 'True')

    def _true(self, parameters):
        self.oracle = defer.Deferred()
        self.oracle.addCallback(self.callback)
        self.oracle.callback(True)

class Turn(Request):
    """A Turn() represents one turn in a game of backgammon. The server will
    notify the bot of a turn to take. That notification is introduced by the
    bot unique id (bot_uid) and composed of an 'order' and parameters.
    An action has to be taken according to the given order.
"""
    def __init__(self, dispatch, manage,):
        self.gnubg = dispatch.protocol.factory.gnubg
        self.expected = dispatch.bot_uid
        self.direction = dispatch.direction
        self._callback = {'double': self.send_double,
                          'move': self.send_move,
                          'take': self.send_take,
                          'accept': self.send_accept,
                          'join': self.send_join,
                          'relax': self.send_thanks,
                         }
        self.label = 'TURN'
        self.sent_request = time.time()
        Request.__init__(self, dispatch, manage,)

    def send_double(self, double):
        log.msg('got double decision: %s' % double, logLevel=logging.DEBUG)
        self.msg_waited = 'double waited for answer %s seconds' % \
                                                time.time() - start_time
        # TODO: resign decision:     gnubg.evaluate()
        #       siehe auch send_move()

        self.send_command({True: 'double', False: 'roll'}[double == 'double'])

    def send_take(self, take):
        log.msg('got take decision: %s' % take, logLevel=logging.DEBUG)
        self.send_command({True: 'accept', False: 'reject'} \
                                                [take in ('take', 'beaver')])

    def send_move(self, move):
        log.msg('got move: %s' % move, logLevel=logging.DEBUG)
        # TODO: resign decision:     gnubg.evaluate()
        #       siehe auch send_double()
        if self.direction == '+':
            mv = ' '.join(['m',] + \
                        [str(25-int(m)) for m in move.strip('()').split(',')])
        else:
            mv = ' '.join(['m',] + move.strip('()').split(','))
        self.send_command(mv)

    def send_accept(self, accept):
        log.msg('got accept decision: %s' % accept, logLevel=logging.DEBUG)
        self.send_command({True: 'accept', False: 'reject'}[accept])
        msg = "tell %s I don't know how to handle resignations, yet. So I " \
                        "simply turn it down. Sorry." % self.dispatch.opponent
        self.send_command(msg)

    def send_join(self, join):
        log.msg('got join', logLevel=logging.DEBUG)
        self.send_command('join')

    def send_thanks(self, congrats):
        opponent = getattr(self.dispatch, 'opponent', False)
        #log.msg('in send_thanks: (%s %s)' % (congrats, type(congrats)), logLevel=TRACE)
        self.dispatch.relax_hook()
        if not opponent:
            log.msg('cannot send thanks: opponent missing!', logLevel=logging.DEBUG)
            return
        if congrats:
            #log.msg('in send_thanks (true): (%s %s)' % (congrats, type(congrats)), logLevel=TRACE)
            msg = "tell %s Congratulations and thanks for playing this " \
                                                        "match :)." % opponent
        else:
            #log.msg('in send_thanks (false): (%s %s)' % (congrats, type(congrats)), logLevel=TRACE)
            msg = "tell %s Thanks for playing this match :)." % opponent
        del self.dispatch.opponent
        log.msg('sending thanks: %s' % msg, logLevel=VERBOSE)
        self.send_command(msg)

    def received(self, message):
        log.msg(self.msg_tests % message[0], logLevel=VERBOSE)
        expected_reaction = message[0].split()
        ret = len(expected_reaction) > 2
        if ret:
            uid, order = expected_reaction[:2]
            parameters = expected_reaction[2:]
            gnubg = self.gnubg.gnubg
            callback = self._callback[order]
            self.sent_action = time.time()
            self.action = Action(order, parameters, gnubg, callback)
            log.msg(self.msg_applies + '+'*40, logLevel=VERBOSE)
            time_used = time.time() - self.sent_request
            log.msg(self.msg_waited % time_used, logLevel=logging.INFO)
            #self.purge() # TODO: erst purgen, wenn der callback stattgefunden hat.
                         #       Das heißt, den purge als callback chain dranhängen.
            Turn(self.dispatch, self.manage,)
            del message[0]
        else:
            log.msg('TURN applies NOT '+'-'*36, logLevel=VERBOSE)
        return ret
