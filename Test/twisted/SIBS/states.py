#!/usr/bin/python
# -*- coding: utf-8 -*-
"""State machine for SIBS.
"""

REV = '$Revision$'

import logging
from version import Version

v = Version()
v.register(__name__, REV)

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
        logging.info('%s: aktiviert mit player %s und Parametern %s)' % (self.name,player,params))
        self.player = player
        self.approved_player = self.player  # This may have to be overwritten
                                            # in special(); may be the opponent.
        self.params = params    # TODO: ich glaub, ich brauch die nur in activate()
                                #       also kein Attribut dieses Objects
        self.results = None
        self.active = True
        self.machine(self)      # self.machine is set by the state machine
        self._special()
        self._chat()
        self._auto_action()

    def deactivate(self,):
        self.active = False

    def action(self, player, cmd, **params):
        check = self._state_check(player, cmd)
        if check == '':                         # action is allowed, only,
            self._action(player, cmd, **params) # when state_check is passed
            self._transit(self.actions[cmd]['follow_up'])
        else:
            self._chat(check)

    def _auto_action(self,):
        if (len(self.actions) == 1):
            k = self.actions.keys()[0]
            if self.actions[k]['auto']:
                logging.info('automatisches cmd: %s' % k)
                self.action(self.player, k)

    def _state_check(self, player, cmd):
        if (player == self.approved_player):
            if self.actions.has_key(cmd):
                return ''
            else:
                return "error: you can't %s" % cmd
        else:
            return "error: it is not your turn to %s" % cmd
        # TODO: hier einen qualifizierten Fehler zurückgeben oder (vermutlich) ''

    def _action(self, player, cmd, **params):
        action = self.actions[cmd]['action']
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
            logging.info('%s: mit Aktivierung fertig' % (self.name,))

class GameStarted(State):
    """State A: game has started."""
    
    def __init__(self,):
        self.name = 'game_started'
        State.__init__(self)

    # automatisch weitergehen (generisch)
    
class TurnStarted(State):
    """State B: a new turn has started."""
    
    def __init__(self,):
        self.name = 'turn_started'
        State.__init__(self)

    def _special(self,):
        self.player = self.player.opponent        # switch players

    # automatisch weitergehen bei no_double oder auto_roll

class Doubled(State):
    """State C: the cube has been turned."""
    
    def __init__(self,):
        self.name = 'doubled'
        State.__init__(self)

    # mir fällt nix ein

class Taken(State):
    """State D: the cube has been taken."""
    
    def __init__(self,):
        self.name = 'taken'
        State.__init__(self)

    # automatisch weitergehen (generisch)        stimmt das? in FIBS prüfen!

class Rolled(State):
    """State E: dice have been rolled."""
    
    def __init__(self,):
        self.name = 'rolled'
        State.__init__(self)

    # check_dice     evtl. automatisch weitergehen

class Moved(State):
    """State F: move has been made."""
    
    def __init__(self,):
        self.name = 'moved'
        State.__init__(self)

    # Spiel zu Ende?   automatisch weitergehen (generisch)

class GameFinished(State):
    """State G: game has ended."""
    
    def __init__(self,):
        self.name = 'finished'
        State.__init__(self)

class StateMachine:
    def __init__(self, states):
        self.states = states
        for s in states:
            self.states[s].machine = self.activate
        logging.info('CONSTRUCTING (%d states)' % len(self.states))

    def start(self, player, **kw):
        logging.info('STARTING   player %s' % player.name)
        self.states['game_started'].activate(player, **kw)

    def action(self, player, cmd, **kw):
        #print 'DEBUG', kw
        logging.info('ACTION   player %s (%s with %s)' % (player.name, cmd, kw))
        self.active.action(player, cmd, **kw)

    def activate(self, state):
        self.active = state
        logging.info('ACTIVATING %s (%s)' % (state.name, state.__doc__))

    def done():
        return self.active.name == 'finished'

class Commands:
    def start(self, player, **params):
        logging.info('start: %s (%s)' % (player.name, params))
        return {}

    def roll(self, player, **params):
        logging.info('roll: %s (%s)' % (player.name, params))
        return {}

    def double(self, player, **params):
        logging.info('double: %s (%s)' % (player.name, params))
        return {}

    def take(self, player, **params):
        logging.info('take: %s (%s)' % (player.name, params))
        return {}

    def drop(self, player, **params):
        logging.info('drop: %s (%s)' % (player.name, params))
        return {}

    def roll(self, player, **params):
        logging.info('roll: %s (%s)' % (player.name, params))
        return {}

    def move(self, player, **params):
        logging.info('move: %s (%s)' % (player.name, params))
        return {}

    def nop(self, player, **params):
        logging.info('nop: %s (%s)' % (player.name, params))
        return {}

    def hand_over(self, player, **params):
        logging.info('hand_over: %s (%s)' % (player.name, params))
        return {}

if __name__ == '__main__':
    from game import Player
    from game import BGMachine

    logging.basicConfig(level=logging.INFO,
                    format='%(name)s %(asctime)s %(levelname)s %(message)s',
                    )
    p1 = Player('white', 'user1', None, 0)
    p2 = Player('black', 'user2', p1, 0)
    p1.opponent = p2
    s = BGMachine(Commands())
    s.start(p1)
    s.action(p1, 'move', move='18-12 12-10')
