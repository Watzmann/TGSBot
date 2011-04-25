#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""Unittests for the game_utilities module."""

import sys
import os
sibs_dir = os.path.dirname(os.getcwd())
os.chdir(sibs_dir)
sys.path.append(sibs_dir)
import unittest
from test_tools import *
from game_utilities import *
import logging

logger.setLevel(logging.ERROR)

class TestBarMovesOnly(unittest.TestCase):

    def setUp(self):
        self.position_25 = [0, 0,0,0,1,4,5, 0,3,0,0,0,0,
                            0,0,0,2,0,0, -7,-5,-3,0,0,0, 0]

##    def tearDown(self):

    def testcheck_bar_1_66(self):
        ret = check_bar_moves((6,6), self.position_25, 1, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], [])
        self.assertEqual(ret['nr_moved_pieces'], 0)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_1_55(self):
        ret = check_bar_moves((5,5), self.position_25, 1, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], [])
        self.assertEqual(ret['nr_moved_pieces'], 0)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_1_33(self):
        ret = check_bar_moves((3,3), self.position_25, 1, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [3, 3, 3])
        self.assertEqual(ret['list_of_moves'], ['bar-22'])
        self.assertEqual(ret['nr_moved_pieces'], 1)
        self.assertEqual(ret['remaining_moves'], 3)
        self.assertEqual(ret['forced_move'], False)
        self.assertEqual(ret['checks_neccessary'], True)

    def testcheck_bar_1_65(self):
        ret = check_bar_moves((6,5), self.position_25, 1, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], [])
        self.assertEqual(ret['nr_moved_pieces'], 0)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_1_62(self):
        ret = check_bar_moves((6,2), self.position_25, 1, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [6,])
        self.assertEqual(ret['list_of_moves'], ['bar-23'])
        self.assertEqual(ret['nr_moved_pieces'], 1)
        self.assertEqual(ret['remaining_moves'], 1)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], True)

    def testcheck_bar_1_21(self):
        ret = check_bar_moves((2,1), self.position_25, 1, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [2, 1])
        self.assertEqual(ret['list_of_moves'], ['bar-23', 'bar-24'])
        self.assertEqual(ret['nr_moved_pieces'], 1)
        self.assertEqual(ret['remaining_moves'], 1)
        self.assertEqual(ret['forced_move'], False)
        self.assertEqual(ret['checks_neccessary'], True)

    def testcheck_bar_2_66(self):
        ret = check_bar_moves((6,6), self.position_25, 2, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], [])
        self.assertEqual(ret['nr_moved_pieces'], 0)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_2_55(self):
        ret = check_bar_moves((5,5), self.position_25, 2, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], [])
        self.assertEqual(ret['nr_moved_pieces'], 0)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_2_33(self):
        ret = check_bar_moves((3,3), self.position_25, 2, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [3, 3])
        self.assertEqual(ret['list_of_moves'], ['bar-22', 'bar-22'])
        self.assertEqual(ret['nr_moved_pieces'], 2)
        self.assertEqual(ret['remaining_moves'], 2)
        self.assertEqual(ret['forced_move'], False)
        self.assertEqual(ret['checks_neccessary'], True)

    def testcheck_bar_2_65(self):
        ret = check_bar_moves((6,5), self.position_25, 2, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], [])
        self.assertEqual(ret['nr_moved_pieces'], 0)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_2_62(self):
        ret = check_bar_moves((6,2), self.position_25, 2, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], ['bar-23'])
        self.assertEqual(ret['nr_moved_pieces'], 1)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_2_21(self):
        ret = check_bar_moves((2,1), self.position_25, 2, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], ['bar-23', 'bar-24'])
        self.assertEqual(ret['nr_moved_pieces'], 2)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_3_66(self):
        ret = check_bar_moves((6,6), self.position_25, 3, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], [])
        self.assertEqual(ret['nr_moved_pieces'], 0)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_3_55(self):
        ret = check_bar_moves((5,5), self.position_25, 3, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], [])
        self.assertEqual(ret['nr_moved_pieces'], 0)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_3_33(self):
        ret = check_bar_moves((3,3), self.position_25, 3, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [3,])
        self.assertEqual(ret['list_of_moves'], ['bar-22', 'bar-22', 'bar-22'])
        self.assertEqual(ret['nr_moved_pieces'], 3)
        self.assertEqual(ret['remaining_moves'], 1)
        self.assertEqual(ret['forced_move'], False)
        self.assertEqual(ret['checks_neccessary'], True)

    def testcheck_bar_3_65(self):
        ret = check_bar_moves((6,5), self.position_25, 3, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], [])
        self.assertEqual(ret['nr_moved_pieces'], 0)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_3_62(self):
        ret = check_bar_moves((6,2), self.position_25, 3, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], ['bar-23'])
        self.assertEqual(ret['nr_moved_pieces'], 1)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_3_21(self):
        ret = check_bar_moves((2,1), self.position_25, 3, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], ['bar-23', 'bar-24'])
        self.assertEqual(ret['nr_moved_pieces'], 2)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_4_66(self):
        ret = check_bar_moves((6,6), self.position_25, 4, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], [])
        self.assertEqual(ret['nr_moved_pieces'], 0)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_4_55(self):
        ret = check_bar_moves((5,5), self.position_25, 4, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], [])
        self.assertEqual(ret['nr_moved_pieces'], 0)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_4_33(self):
        ret = check_bar_moves((3,3), self.position_25, 4, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], ['bar-22', 'bar-22', 'bar-22', 'bar-22'])
        self.assertEqual(ret['nr_moved_pieces'], 4)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_4_65(self):
        ret = check_bar_moves((6,5), self.position_25, 4, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], [])
        self.assertEqual(ret['nr_moved_pieces'], 0)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_4_62(self):
        ret = check_bar_moves((6,2), self.position_25, 4, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], ['bar-23'])
        self.assertEqual(ret['nr_moved_pieces'], 1)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_4_21(self):
        ret = check_bar_moves((2,1), self.position_25, 4, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], ['bar-23', 'bar-24'])
        self.assertEqual(ret['nr_moved_pieces'], 2)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_5_66(self):
        ret = check_bar_moves((6,6), self.position_25, 5, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], [])
        self.assertEqual(ret['nr_moved_pieces'], 0)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_5_55(self):
        ret = check_bar_moves((5,5), self.position_25, 5, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], [])
        self.assertEqual(ret['nr_moved_pieces'], 0)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_5_33(self):
        ret = check_bar_moves((3,3), self.position_25, 5, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], ['bar-22', 'bar-22', 'bar-22', 'bar-22'])
        self.assertEqual(ret['nr_moved_pieces'], 4)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_5_65(self):
        ret = check_bar_moves((6,5), self.position_25, 5, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], [])
        self.assertEqual(ret['nr_moved_pieces'], 0)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_5_62(self):
        ret = check_bar_moves((6,2), self.position_25, 5, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], ['bar-23'])
        self.assertEqual(ret['nr_moved_pieces'], 1)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)

    def testcheck_bar_5_21(self):
        ret = check_bar_moves((2,1), self.position_25, 5, 25)
        self.assertEqual(len(ret), 6)
        self.assertEqual(ret['my_dice'], [])
        self.assertEqual(ret['list_of_moves'], ['bar-23', 'bar-24'])
        self.assertEqual(ret['nr_moved_pieces'], 2)
        self.assertEqual(ret['remaining_moves'], 0)
        self.assertEqual(ret['forced_move'], True)
        self.assertEqual(ret['checks_neccessary'], False)


# testcases
##
##bar: ein checker draußen, kommt rein
##     ein checker draußen, kommt nicht rein
##     zwei checker draußen, kommt rein
##     zwei checker draußen, einer kommt rein
##     zwei checker draußen, kommt nicht rein
##     drei checker draußen, ....
##     genauso für den gegnerischen spieler

class TestBoardMovesOnly(unittest.TestCase):

    def setUp(self):
        self.position_25 = [0, 0,0,0,1,4,1, 0,3,0,-4,-2,0,
                               0,0,0,2,0,0, -7,-5,-3,0,0,0, 0]
        self.position_50 = [0, 2,0,-1,2,2,2, 0,2,0,0,0,0,
                               0,0,1,1,1,0, 1,0,0,-7,1,-7, 0]
##            {'dice':[(5,1), (1,5)],
##             
##             'dir': {'home':25, 'bar':0}, 'bar': [0,]},
        self.position_75 = [0, 2,0,0,2,2,2, 0,2,0,0,0,0,
                               0,0,1,1,1,0, 1,0,0,-7,1,-7, 0]
##            {'dice':[(6,3),],
##             'dir': {'home':25, 'bar':0}, 'bar': [1,]},
        self.ox_0 = OX(0, 0)
        self.ox_25 = OX(25, 0)

##    def tearDown(self):

    def testcheck_25_66(self):
        ret = check_board_moves((6,6,6,6), self.position_25[1:-1], 4, self.ox_25)
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['list_of_moves'], {6: ['8-2', '8-2', '8-2']})
        self.assertEqual(ret['nr_moved_pieces'], 3)

    def testcheck_25_55(self):
        ret = check_board_moves((5,5,5,5), self.position_25[1:-1], 4, self.ox_25)
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['list_of_moves'], {5: ['6-1', '8-3', '8-3', '8-3']})
        self.assertEqual(ret['nr_moved_pieces'], 4)

    def testcheck_25_33(self):
        ret = check_board_moves((3,3,3,3), self.position_25[1:-1], 4, self.ox_25)
        self.assertEqual(len(ret),2)
        self.assertEqual(ret['list_of_moves'], {3: ['4-1', '5-2', '5-2', '5-2']})
        self.assertEqual(ret['nr_moved_pieces'], 4)

    def testcheck_25_65(self):
        ret = check_board_moves((6,5), self.position_25[1:-1], 2, self.ox_25)
        self.assertEqual(len(ret),2)
        self.assertEqual(ret['list_of_moves'], {5: ['6-1'], 6: ['8-2']})
        self.assertEqual(ret['nr_moved_pieces'], 2)

    def testcheck_25_62(self):
        ret = check_board_moves((6,2), self.position_25[1:-1], 2, self.ox_25)
        self.assertEqual(len(ret),2)
        self.assertEqual(ret['list_of_moves'], {2: ['4-2'], 6: ['8-2']})
        self.assertEqual(ret['nr_moved_pieces'], 2)

    def testcheck_25_21(self):
        ret = check_board_moves((2,1), self.position_25[1:-1], 2, self.ox_25)
        self.assertEqual(len(ret),2)
        self.assertEqual(ret['list_of_moves'], {1: ['2-1'], 2: ['4-2']})
        self.assertEqual(ret['nr_moved_pieces'], 2)

    def testcheck_50_51(self):
        ret = check_board_moves((5,1), self.position_50[1:-1], 2, self.ox_0)
        self.assertEqual(len(ret),2)
        self.assertEqual(ret['list_of_moves'], {1: ['22-23']})
        self.assertEqual(ret['nr_moved_pieces'], 1)

    def testcheck_50_15(self):
        ret = check_board_moves((1,5), self.position_50[1:-1], 2, self.ox_0)
        self.assertEqual(len(ret),2)
        self.assertEqual(ret['list_of_moves'], {1: ['22-23']})
        self.assertEqual(ret['nr_moved_pieces'], 1)

class TestCheckRoll(unittest.TestCase):

    def setUp(self):
        self.position_25 = [0, 0,0,0,1,4,1, 0,3,0,-4,-2,0,
                               0,0,0,2,0,0, -7,-5,-3,0,0,0, 0]
        self.position_50 = [0, 2,0,-1,2,2,2, 0,2,0,0,0,0,
                               0,0,1,1,1,0, 1,0,0,-7,1,-7, 0]
##            {'dice':[(5,1), (1,5)],
##             
##             'dir': {'home':25, 'bar':0}, 'bar': [0,]},
        self.position_75 = [0, 2,0,0,2,2,2, 0,2,0,0,0,0,
                               0,0,1,1,1,0, 1,0,0,-7,1,-7, 0]
##            {'dice':[(6,3),],
##             'dir': {'home':25, 'bar':0}, 'bar': [1,]},
        self.dir_0 = {'home':25, 'bar':0}
        self.dir_25 = {'home':0, 'bar':25}
        self.ox_0 = OX(0, 0)
        self.ox_25 = OX(25, 0)

##    def tearDown(self):

    def testcheck_25_66(self):
        ret = check_roll((6,6), self.position_25, 0, self.dir_25, self.ox_25)
        self.assertEqual(len(ret), 3)
        self.assertEqual(ret['list_of_moves'], ['8-2', '8-2', '8-2'])
        self.assertEqual(ret['nr_pieces'], 3)
        self.assertEqual(ret['forced_move'], True)

    def testcheck_25_55(self):
        ret = check_roll((5,5), self.position_25, 0, self.dir_25, self.ox_25)
        self.assertEqual(len(ret), 3)
        self.assertEqual(ret['list_of_moves'], ['6-1', '8-3', '8-3', '8-3'])
        self.assertEqual(ret['nr_pieces'], 4)
        self.assertEqual(ret['forced_move'], True)

    def testcheck_25_33(self):
        ret = check_roll((3,3), self.position_25, 0, self.dir_25, self.ox_25)
        self.assertEqual(len(ret), 3)
        self.assertEqual(ret['list_of_moves'], ['4-1', '5-2', '5-2', '5-2'])
        self.assertEqual(ret['nr_pieces'], 4)
        self.assertEqual(ret['forced_move'], False)

    def testcheck_25_65(self):
        ret = check_roll((6,5), self.position_25, 0, self.dir_25, self.ox_25)
        self.assertEqual(len(ret), 3)
        self.assertEqual(ret['list_of_moves'], ['6-1', '8-2'])
        self.assertEqual(ret['nr_pieces'], 2)
        self.assertEqual(ret['forced_move'], False)

    def testcheck_25_62(self):
        ret = check_roll((6,2), self.position_25, 0, self.dir_25, self.ox_25)
        self.assertEqual(len(ret), 3)
        self.assertEqual(ret['list_of_moves'], ['4-2', '8-2'])
        self.assertEqual(ret['nr_pieces'], 2)
        self.assertEqual(ret['forced_move'], False)

    def testcheck_25_21(self):
        ret = check_roll((2,1), self.position_25, 0, self.dir_25, self.ox_25)
        self.assertEqual(len(ret), 3)
        self.assertEqual(ret['list_of_moves'], ['2-1', '4-2'])
        self.assertEqual(ret['nr_pieces'], 2)
        self.assertEqual(ret['forced_move'], False)

    def testcheck_50_51(self):
        ret = check_roll((5,1), self.position_50, 0, self.dir_0, self.ox_0)
        self.assertEqual(len(ret), 3)
        self.assertEqual(ret['list_of_moves'], ['22-23',])
        self.assertEqual(ret['nr_pieces'], 1)
        self.assertEqual(ret['forced_move'], True)

    def testcheck_50_15(self):
        ret = check_roll((1,5), self.position_50, 0, self.dir_0, self.ox_0)
        self.assertEqual(len(ret), 3)
        self.assertEqual(ret['list_of_moves'], ['22-23',])
        self.assertEqual(ret['nr_pieces'], 1)
        self.assertEqual(ret['forced_move'], True)

    def testcheck_bar_01(self):
        position = [0, 0,2,0,2,2,3, 1,0,0,0,0,0,
                       0,0,0,0,0,0, 0,0,-1,-3,-3,-2, 0]
        ret = check_roll((4,5), position, 5, self.dir_25, self.ox_25)
        self.assertEqual(len(ret), 3)
        self.assertEqual(ret['list_of_moves'], ['bar-21', 'bar-20'])
        self.assertEqual(ret['nr_pieces'], 2)
        self.assertEqual(ret['forced_move'], True)

    def testcheck_bar_02(self):
        position = [0, 0,1,2,2,2,2, 0,3,0,0,0,1,
                       0,0,0,0,0,0, -2,2,-2,-5,-2,-3, 0]
        ret = check_roll((1,6), position, 1, self.dir_0, self.ox_0)
        self.assertEqual(len(ret), 3)
        self.assertEqual(ret['list_of_moves'], ['bar-1', '1-7'])
        self.assertEqual(ret['nr_pieces'], 2)
        self.assertEqual(ret['forced_move'], True)

    def testcheck_bearoff_01(self):
        position = [0, 3,4,0,0,-1,0, 0,0,0,0,0,0,
                       0,0,0,0,0,0, 0,0,-2,-6,-2,-4, 0]
        ret = check_roll((3,5), position, 0, self.dir_25, OX(25, 8))
        self.assertEqual(len(ret), 3)
        self.assertEqual(ret['list_of_moves'], ['2-off', '2-off'])
        self.assertEqual(ret['nr_pieces'], 2)
        self.assertEqual(ret['forced_move'], True)

class TestCheckGreedy(unittest.TestCase):

    def setUp(self):
        self.position_25 = [0, 8,2,2,0,0,0, 0,0,0,0,0,0,
                               0,0,0,0,0,0, 0,0,0,-1,-1,-2, 0]
        self.position_50 = [0, 1,2,0,0,0,0, 0,0,0,0,0,0,
                               0,0,0,0,0,0, 0,0,0,0,-1,-2, 0]
        self.position_75 = [0, 0,0,0,1,0,0, 0,0,0,0,0,0,
                               0,0,0,0,0,0, 0,-1,0,0,0,0, 0]
        
        # now some testcases destilled from livetest
        self.position_contact_25 = [0, 0,0,0,0,1,3, 0,0,1,0,0,0,
                                       1,0,0,0,0,2, -2,-6,3,-2,-4,4, 0]
##    def tearDown(self):

    def testgreedy_25_23(self):
        ret = greedy((2,3), self.position_25, OX(25,3))
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['moves'], ['3-0', '2-0'])
        self.assertEqual(ret['greedy_possible'], True)
        ret = greedy((2,3), self.position_25, OX(0,11))
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['moves'], ['22-off', '23-off'])
        self.assertEqual(ret['greedy_possible'], True)

    def testgreedy_25_32(self):
        ret = greedy((3,2), self.position_25, OX(25,3))
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['moves'], ['3-0', '2-0'])
        self.assertEqual(ret['greedy_possible'], True)
        ret = greedy((3,2), self.position_25, OX(0,11))
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['moves'], ['22-off', '23-off'])
        self.assertEqual(ret['greedy_possible'], True)

    def testgreedy_25_42(self):
        ret = greedy((4,2), self.position_25, OX(25,3))
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['moves'], ['3-0', '2-0'])
        self.assertEqual(ret['greedy_possible'], True)
        ret = greedy((4,2), self.position_25, OX(0,11))
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['moves'], ['22-off', '23-off'])
        self.assertEqual(ret['greedy_possible'], True)

    def testgreedy_25_45(self):
        ret = greedy((4,5), self.position_25, OX(25,3))
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['moves'], ['3-0', '3-0'])
        self.assertEqual(ret['greedy_possible'], True)
        ret = greedy((4,5), self.position_25, OX(0,11))
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['moves'], ['22-off', '23-off'])
        self.assertEqual(ret['greedy_possible'], True)

    def testgreedy_25_55(self):
        ret = greedy((5,5), self.position_25, OX(25,3))
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['moves'], ['3-0', '3-0', '2-0', '2-0'])
        self.assertEqual(ret['greedy_possible'], True)
        ret = greedy((5,5), self.position_25, OX(0,11))
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['moves'], ['22-off', '23-off', '24-off', '24-off'])
        self.assertEqual(ret['greedy_possible'], True)

    def testgreedy_25_33(self):
        ret = greedy((3,3), self.position_25, OX(25,3))
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['moves'], ['3-0', '3-0', '2-0', '2-0'])
        self.assertEqual(ret['greedy_possible'], True)
        ret = greedy((3,3), self.position_25, OX(0,11))
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['moves'], ['22-off', '23-off', '24-off', '24-off'])
        self.assertEqual(ret['greedy_possible'], True)

    def testgreedy_50_33(self):
        ret = greedy((3,3), self.position_50, OX(25,12))
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['moves'], ['2-0', '2-0', '1-0'])
        self.assertEqual(ret['greedy_possible'], True)
        ret = greedy((3,3), self.position_50, OX(0,12))
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['moves'], ['23-off', '24-off', '24-off'])
        self.assertEqual(ret['greedy_possible'], True)

    def testgreedy_50_61(self):
        ret = greedy((6,1), self.position_50, OX(25,12))
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['moves'], ['2-0', '1-0'])
        self.assertEqual(ret['greedy_possible'], True)
        ret = greedy((6,1), self.position_50, OX(0,12))
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['moves'], ['23-off', '24-off'])
        self.assertEqual(ret['greedy_possible'], True)

    def testgreedy_75_61(self):
        ret = greedy((6,1), self.position_75, OX(25,12))
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['moves'], ['4-0',])
        self.assertEqual(ret['greedy_possible'], True)
        ret = greedy((6,1), self.position_75, OX(0,12))
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['moves'], ['20-off',])
        self.assertEqual(ret['greedy_possible'], True)

    def testgreedy_75_41(self):
        ret = greedy((4,1), self.position_75, OX(25,12))
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['moves'], ['4-0',])
        self.assertEqual(ret['greedy_possible'], True)
        ret = greedy((4,1), self.position_75, OX(0,12))
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['moves'], ['20-24', '24-off'])
        self.assertEqual(ret['greedy_possible'], True)

    def testgreedy_contact_25_15(self):
        ret = greedy((1,5), self.position_contact_25, OX(0,1))
        print ret
        self.assertEqual(len(ret), 2)
        self.assertEqual(ret['moves'], ['4-0',])
        self.assertEqual(ret['greedy_possible'], False)

if __name__ == "__main__":
    do_suites = (len(sys.argv) > 1) and (sys.argv[1] == 'suites')

    if not do_suites:
        test = 'testgreedy_contact_25_15' #'testcheck_bearoff_01'
        run_test(TestCheckGreedy(test))
    else:
        run_suites(globals())
