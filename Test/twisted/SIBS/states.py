#!/usr/bin/python
# -*- coding: utf-8 -*-
"""State machine for SIBS.
"""

REV = '$Revision$'

from version import Version

v = Version()
v.register(__name__, REV)

global VERBOSE
VERBOSE = False

def talk(msg):
    if VERBOSE:
        print msg
        
class State:
    """Base class for states in this state machine."""
    
    def __init__(self, actions):
        self.active = False
        if actions is None:
            self.actions = {}
        else:
            self.actions = dict(zip(actions, ({'action': None},)*len(actions)))

    def activate(self, player, **params):
        """Activates this state.
    player:     class Player
    params:     **kw
    """
        self.player = player
        self.approved_player = self.player  # This may have to be overwritten
                                            # in special(); may be the opponent.
        self.params = params    # TODO: ich glaub, ich brauch die nur in activate()
                                #       also kein Attribut dieses Objects
        self.results = None
        self.active = True
        self.machine(self)
        self._special()
        self._chat()

    def deactivate(self,):
        self.active = False

    def action(self, player, cmd, **params):
        check = self._state_check(player, cmd)
        if check == '':                         # action is allowed, only,
            self._action(player, cmd, **params) # when state_check is passed
            self._transit(self.actions[cmd]['follow_up'])
        else:
            self._chat(check)

    def _state_check(self, player, cmd):
        if (player == self.approved_player):
            if self.actions.has_key(cmd):
                return ''
            else:
                return "error: you can't %s" % cmd
        else:
            return "error: it is not your turn to %s" % cmd
        # TODO: hier einen qualifizierten Fehler zurückgeben oder (vermutlich) ''

    def _action(self, player, cmd):
        action = actions[cmd]['action'] # set attribute instead of return to be
        self.result = action(player, self.params) # able to do some processing
        
    def _transit(self, next_state):
        self.deactivate()
        next_state.activate(player, self.result) # parameters come from _action

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

class GameStarted(State):
    """State A: game has started."""
    
    def __init__(self, actions,):
        self.name = 'game_started'
        State.__init__(self, actions)

class TurnStarted(State):
    """State B: a new turn has started."""
    
    def __init__(self, actions,):
        self.name = 'turn_started'
        State.__init__(self, actions)

    def _special(self,):
        self.player = 1
        #switch players

class Doubled(State):
    """State C: the cube has been turned."""
    
    def __init__(self, actions,):
        self.name = 'doubled'
        State.__init__(self, actions)

class Taken(State):
    """State D: the cube has been taken."""
    
    def __init__(self, actions,):
        self.name = 'taken'
        State.__init__(self, actions)

class Rolled(State):
    """State E: dice have been rolled."""
    
    def __init__(self, actions,):
        self.name = 'rolled'
        State.__init__(self, actions)

class Moved(State):
    """State F: move has been made."""
    
    def __init__(self, actions,):
        self.name = 'moved'
        State.__init__(self, actions)

class GameFinished(State):
    """State G: game has ended."""
    
    def __init__(self, actions,):
        self.name = 'finished'
        State.__init__(self, actions)

class StateMachine:
    def __init__(self,):
        self.states = dict((        # TODO: es sieht etwas inkonsequent aus,
                                    # hier die actions anzulegen, sie dann aber
                                    # weiter unten zu erweitern;
                                    # das kann man doch alles unten machen, dann
                                    # gibt es keine Abhängigkeiten von Code
            ('game_started', GameStarted(('start',))),
            ('turn_started', TurnStarted(('roll', 'double'))),
            ('doubled', Doubled(('take', 'pass'))),
            ('taken', Taken(('roll',))),
            ('rolled', Rolled(('move', 'cant_move',))),
            ('moved', Moved(('turn', 'win'))),
            ('finished', GameFinished(None)),
            ))
        s = self.states
        model = {'game_started': (('start', (s['rolled'], True)),),
                 'turn_started': (('roll', (s['rolled'], False)),
                                  ('double', (s['doubled'], False)),),
                 'doubled': (('take', (s['taken'], False)),
                             ('pass', (s['finished'], False)),),
                 'taken': (('roll', (s['rolled'], True)),),
                 'rolled': (('move', (s['moved'], False)),
                            ('cant_move', (s['turn_started'], True)),),
                 'moved': (('turn', (s['taken'], False)),
                             ('win', (s['finished'], True)),),
                }
        for s in model:
            for k,v in model[s]:
                self.states[s].actions[k]['follow_up'] = v[0]
                self.states[s].actions[k]['auto'] = v[1]
            self.states[s].machine = self.activate

    def start(self, player, **kw):
        self.states['game_started'].activate(player, **kw)

    def action(self, player, cmd, **kw):
        self.active.action(player, cmd, **kw)

    def activate(self, state):
        self.active = state
        talk('%s: aktiviert (%s)' % (state.name, state.__doc__))

    def done():
        return self.active.name == 'finished'

from game import Player

if __name__ == '__main__':
    VERBOSE = True
    p1 = Player('white', 'user1', None, 0)
    p2 = Player('black', 'user2', p1, 0)
    p1.opponent = p2
    s = StateMachine()
    s.start(p1)
    s.action(p1, 'move', move='18-12 12-10')
