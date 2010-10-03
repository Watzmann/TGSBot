#!/usr/bin/python
# -*- coding: utf-8 -*-
"""State machine for SIBS.
"""

REV = '$Revision$'

from version import Version

v = Version()
v.register(__name__, REV)

class State:
    """Base class for states in this state machine."""
    
    def __init__(self,):
        self.active = False

    def activate(self, player, params):
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
        self._special()
        self._chat()

    def deactivate(self,):
        self.active = False

    def action(self, player, cmd):
        if self._state_check(player, cmd):      # action is allowed, only,
            self._action(player, cmd)           # when state_check is passed
            self._transit()

    def _state_check(self, player, cmd):
        if (player == self.approved_player) and actions.has_key(cmd):
            #self._action(player, cmd)
        # TODO: hier einen qualifizierten Fehler zurückgeben oder (vermutlich) ''

    def _action(self, player, cmd):
        action = actions[cmd]          # set attribute instead of return to be
        self.result = action(player, self.params) # able to do some processing
        
    def _transit(self, next_state):
        self.deactivate()
        next_state.activate(player, self.result) # parameters come from _action

    def _special(self,):
        """Method intended for being overwritten. _special() is being
    called during activation phase.
    """
        pass

    def _chat(self,):
        """Send messages to the players during activation phase. This Method
    is intended for being overwritten.
    """
        pass

class Started(State):
    """State A: game has started."""
    
    def __init__(self,):
        self.name = 'started'
        State.__init__(self)


class StateMachine:
    def __init__(self,):
        cube = {'player_on_turn': None, 'next': }

    def next_state(self,):
        pass
    
if __name__ == '__main__':
    s = StateMachine()
    for c in sys.argv[1:]:
        for h in h.help_(c):
            print h,
            
