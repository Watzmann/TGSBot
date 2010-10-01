#!/usr/bin/python
# -*- coding: utf-8 -*-
"""State machine for SIBS.
"""

REV = '$Revision$'

from version import Version

v = Version()
v.register(__name__, REV)

class State:
    def __init__(self,):
        self.active = False

    def activate(self, player, params):
        pass

    def deactivate(self,):
        pass

    def state_check(self,):
        pass

    def action(self, player, cmd):
        self.result = actions[cmd]

    def transit(self, next_state):
        self.deactivate()
        next_state.activate(player, params) # die params kommen von der action

    def chat(self,):
        pass

    def special(self,):
        pass

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
            
