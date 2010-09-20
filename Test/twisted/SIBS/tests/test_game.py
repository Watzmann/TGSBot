#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""Unittests for the game module."""

import sys
import os
sibs_dir = os.path.dirname(os.getcwd())
os.chdir(sibs_dir)
sys.path.append(sibs_dir)
import unittest
from test_tools import *
from game import GamesList
from dev_game import Spiel   # TODO: eigenes Spiel bauen (wegen der Sequenz)
from dev_game import get_game

log = GamesList()
sequence_1 = (
((3, 6), []),
((6, 3), []),
((1, 6), ['bar-1',]),
((6, 1), ['bar-1',]),
((1, 2), ['bar-1', 'bar-2']),
((2, 1), ['bar-2', 'bar-1']),
)

class TestGame(unittest.TestCase):

    def setUp(self):
        self.spiel = Spiel(1)
        self.id1, p1 = get_game('p1')
        self.id2, p2 = get_game('p2')

    def testbar_roll_in(self):
        self.spiel.dice_and_moves(sequence_1, self.id1)
        turn = self.spiel.whos_turn()
        turn = self.spiel.hand_over()
        game, player = log.get(turn)
        gc = game.control
        gc.position = [-1, 0,0,2,2,2,3, 0,0,0,0,1,0,
                        3,1,-1,0,-2,-3, -3,1,0,-2,-2,0, 0]
        gc.set_position()
        gc.bar = {'p1':0, 'p2':1}
        gc.set_move()
        for d in range(6):
            gc.roll(player)
            ist = gc.possible_moves[1]
            soll = self.spiel.get_move()
            dice = gc.dice_roll
            print '####', '%s - soll: %s   ist: %s' % (dice, soll, ist)
            self.assert_(ist == soll, '%s - soll: %s   ist: %s' % \
                                                         (dice, soll, ist))
            print '='*80

# testcases
##
##bar: ein checker draußen, kommt rein
##     ein checker draußen, kommt nicht rein
##     zwei checker draußen, kommt rein
##     zwei checker draußen, einer kommt rein
##     zwei checker draußen, kommt nicht rein
##     drei checker draußen, ....
##     genauso für den gegnerischen spieler

if __name__ == "__main__":
    do_suites = (len(sys.argv) > 1) and (sys.argv[1] == 'suites')

    if not do_suites:
        run_test(TestGame('testbar_roll_in'))
    else:
        run_suites(globals())
