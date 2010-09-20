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
from game import Board

class TestBoard(unittest.TestCase):

##    def setUp(self):
##        self.spiel = Spiel(1)
##        self.id1, p1 = get_game('p1')
##        self.id2, p2 = get_game('p2')

    def testload(self):
        b = Board()
        board = ("board:You:dortdann:1:1:2:-1:0:0:2:2:2:3:0:0:0:0:1:0:3:1:-1:0:-2:-3:-3:1:0:-2:-2:0:0:-1:0:0:1:6:1:1:1:0:1:-1:0:25:0:0:0:1:2:0:0:0",
                 "board:You:kawasaki:1:0:0:0:-2:0:0:0:0:5:0:3:0:0:0:-5:5:0:0:0:-3:0:-5:0:0:0:0:2:0:-1:2:6:0:0:1:1:1:0:-1:1:25:0:0:0:0:0:2:0:0:0",
                 )
        for i in board:
            b.load(i)
            b2 = b.board_sl(b.get_act_player())
            self.assertEqual(i, b2)

if __name__ == "__main__":
    do_suites = (len(sys.argv) > 1) and (sys.argv[1] == 'suites')

    if not do_suites:
        run_test(TestBoard('testload'))
    else:
        run_suites(globals())
