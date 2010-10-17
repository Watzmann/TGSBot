#!/usr/bin/python
# -*- coding: utf-8 -*-
"""State machine for SIBS.
"""

REV = '$Revision$'

import logging
from version import Version

v = Version()
v.register(__name__, REV)

TRACE = 15
logging.addLevelName(TRACE, 'TRACE')
logging.basicConfig(level=logging.INFO,
                format='%(name)s %(asctime)s %(levelname)s %(message)s',
                )
logger = logging.getLogger('states')

class State:
    """Base class for states in this state machine."""
    
    def __init__(self,):
        self.active = False
        self.actions = {}

    def activate(self, player, **params):
        """Activates this state.
    player:     class Player
    params:     **kw
    """
        logger.log(TRACE, '%s: wird aktiviert mit player %s und Parametern %s)' % (self.name,player.name,params))
        self.player = player
        self.approved_player = self.player  # This may have to be overwritten
                                            # in special(); may be the opponent.
        self.params = params
        self.results = None
        self.active = True
        self.machine(self)      # self.machine is set by the state machine
        self._special()
        self._chat()
        buchstabe = self.__doc__.split()[1]
        logger.info('%s %s: player %s ,Parameter %s)' % (buchstabe, self.name,player.name,params))
        self._auto_action()

    def deactivate(self,):
        self.active = False

    def action(self, player, cmd, **params):
        check = self._state_check(player, cmd)
        if check == '':                         # action is allowed, only,
            self._action(player, cmd, **params) # when state_check is passed
            self._transit(self.actions[cmd]['follow_up'])
        else:
            self._chat(check)   # TODO: das muss wohl ein _error_chat sein,
                                #       das nur den player adressiert.

    def _auto_action(self,):
        """Method intended for being overwritten. _auto_action() is the last
    method being called during activation phase.
    Default behavior is to perform an action automatically if it is the only
    action and is flagged as 'auto'.
    """
        if (len(self.actions) == 1):
            k = self.actions.keys()[0]
            if self.actions[k]['auto']:
                logger.log(TRACE, 'automatisch standard cmd: %s' % k)
                self.action(self.player, k, self.params)

    def _state_check(self, player, cmd):
        if (player.name == self.approved_player.name):
            if self.actions.has_key(cmd):
                return ''
            else:
                return "error: you can't %s" % cmd
        else:
            return "error: it is not your turn to %s" % cmd
        # TODO: hier einen qualifizierten Fehler zurückgeben oder (vermutlich) ''

    def _action(self, player, cmd, **params):
        action = self.actions[cmd]['action']
        logger.debug('calling %s with %s' % (action, params))
        self.result = action(player, **params)
        # set attribute instead of return to be able to do some processing
        
    def _transit(self, next_state):
        self.deactivate()
        next_state.activate(self.player, **self.result)
        # parameters come from _action

    def _special(self,):
        """Method intended for being overwritten. _special() is being
    called during activation phase.
"""
        pass

    def _chat(self, msg=None):
        """Send messages to the players during activation phase. This Method
    is intended for being overwritten.
    """
        if not msg is None:
            print msg
        else:
            logger.log(TRACE, '%s: hat nix zu chatten' % (self.name,))

class GameStarted(State):
    """State A: game has started."""
    
    def __init__(self,):
        self.name = 'game_started'
        State.__init__(self)

    def _action(self, player, cmd, **params):
        """Special treatment while starting a game. Set active player as a
    result of starting rolls.
    """
        action = self.actions[cmd]['action']
        logger.debug('calling %s with %s' % (action, params))
        self.result = action(player, **{})
        self.player = self.result['turn']

    # +++++++++++ start
    # you rolled, he rolled
    # it is you turn; he makes the first move
    # board
    
class TurnStarted(State):
    """State B: a new turn has started."""
    
    def __init__(self,):
        self.name = 'turn_started'
        State.__init__(self)

    # automatisch weitergehen bei no_double oder auto_roll
    #  sonst
    # please roll or double
    # +++++++++++ roll, double

    def _auto_action(self,):
        """Decide whether player may double and automatically perform
    'roll (state H)' if he may not.
    """
        if not self.params['may_double']:
            logger.log(TRACE, 'automatisches cmd: %s' % 'roll')
            self.action(self.player, 'roll')

class Doubled(State):
    """State C: the cube has been turned."""
    
    def __init__(self,):
        self.name = 'doubled'
        State.__init__(self)

    # you double, please wait; he doubles, please accept
    # +++++++++++ take, drop

class Taken(State):
    """State D: the cube has been taken."""
    
    def __init__(self,):
        self.name = 'taken'
        State.__init__(self)

    # you accept, the cube shows; he accepts, the cube shows
    # +++++++++++ roll      (auto)

class Rolled(State):
    """State H: dice have been rolled."""
    
    def __init__(self,):
        self.name = 'rolled'
        State.__init__(self)

    # he rolls; you roll
    # +++++++++++ check      (auto)
    # please move n pieces          könnte doch auch in Checked sein?

class TurnFinished(State):
    """State I: this turn has been finished."""
    
    def __init__(self,):
        self.name = 'turn_finished'
        State.__init__(self)

    # send board
    # +++++++++++ hand_over      (auto)

##    def _special(self,):
##        self.player = self.player.opponent        # switch players

##    def _chat(self, msg=None):
##        self.player.board_player()
##        self.player.board_opponent()

    def _transit(self, next_state):
        self.deactivate()
        self.result = {'may_double': False}
        next_state.activate(self.player.opponent, **self.result)
        # parameters come from _action

class Checked(State):
    """State E: dice have been checked."""
    
    def __init__(self,):
        self.name = 'checked'
        State.__init__(self)

    # +++++++++++ move      (evtl. auto)

class Moved(State):
    """State F: move has been made."""
    
    def __init__(self,):
        self.name = 'moved'
        State.__init__(self)

    def _chat(self, msg=None):
        if msg is None:
            msg = '%s moves %s' % (self.player.name,
                                   ' '.join(self.params['moved']))
        self.player.chat_opponent(msg)

    # he moves.....
    #  oder
    # Spiel zu Ende?   automatisch weitergehen (generisch)
    # +++++++++++ handover, nop      (auto)
    # board

    def _auto_action(self,):
        """Decide whether game is finished and automatically perform
    'nextturn (state B)' or 'wingame (state G)'.
    """
        follower = {True: 'win', False: 'turn'}[self.params['finished']]
        if self.actions[follower]['auto']:
            logger.log(TRACE, 'automatisches cmd: %s' % follower)
            self.action(self.player, follower)

class GameFinished(State):
    """State G: game has ended."""
    
    def __init__(self,):
        self.name = 'finished'
        State.__init__(self)

    # you win 1 point......

class StateMachine:
    """Container for a bundle of states. Hands out some controls. Controls
which state is active.
"""
    def __init__(self, states):
        self.states = states
        for s in states:
            self.states[s].machine = self._activate
        logger.log(TRACE, 'CONSTRUCTING (%d states)' % len(self.states))

    def start(self, player, **kw):
        """Allows to start the state machine."""
        logger.log(TRACE, 'STARTING   player %s' % player.name)
        self.states['game_started'].activate(player, **kw)

    def action(self, player, cmd, **kw):
        """Allows control to send actions, taken by the players."""
        #print 'DEBUG', kw
        logger.log(TRACE, 'ACTION   player %s (%s with %s)' % (player.name, cmd, kw))
        self.active.action(player, cmd, **kw)

    def _activate(self, state):
        """States activate themselves using this method."""
        self.active = state
        logger.log(TRACE, 'ACTIVATING %s (%s)' % (state.name, state.__doc__))

    def done():
        """True, if game is finished."""
        return self.active.name == 'finished'

class Commands:
    def __init__(self, player1):
        self.player1 = player1
        
    def _start(self, p, **kw):
        logger.log(TRACE, 'stub cmd +++++ _start')
        return {'roll': (3,5), 'turn': self.player1}

    def roll(self, player, **params):
        logger.log(TRACE, 'stub cmd +++++ roll: %s (%s)' % (player.name, params))
        return {}

    def double(self, player, **params):
        logger.log(TRACE, 'stub cmd +++++ double: %s (%s)' % (player.name, params))
        return {}

    def take(self, player, **params):
        logger.log(TRACE, 'stub cmd +++++ take: %s (%s)' % (player.name, params))
        return {}

    def drop(self, player, **params):
        logger.log(TRACE, 'stub cmd +++++ drop: %s (%s)' % (player.name, params))
        return {}

    def check_roll(self, player, **params):
        logger.log(TRACE, 'stub cmd +++++ check_roll: %s (%s)' % (player.name, params))
        return {}

    def _move(self, player, **params):
        logger.log(TRACE, 'stub cmd +++++ _move: %s (%s)' % (player.name, params))
        return {'moved': ['24-23', '13-7'], 'finished': False}

    def nop(self, player, **params):
        logger.log(TRACE, 'stub cmd +++++ nop: %s (%s)' % (player.name, params))
        return {}

    def hand_over(self, player, **params):
        logger.log(TRACE, 'stub cmd +++++ hand_over: %s (%s)' % (player.name, params))
        return {'may_double': False}

class TestUser:
    def __init__(self, name):
        self.name = name

    def chat(self, msg):
        print 'CHAT -> %s:' % self.name, msg
        
if __name__ == '__main__':
    from game import Player
    from game import BGMachine

    logger.setLevel(TRACE)

    p1 = Player(TestUser('white'), None, 0)
    p2 = Player(TestUser('black'), p1, 0)
    p1.set_opponent(p2)
    s = BGMachine(Commands(p1))
    logger.info('-'*40 + ' start')
    s.start(p1)
    logger.info('-'*40 + ' move 18-12 12-10')
    s.action(p1, 'move', move='18-12 12-10')
    logger.info('-'*40 + ' ??')
