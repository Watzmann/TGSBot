#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
u"""Unittests für bao"""

import sys
import os
sys.path.append(os.getcwd())
import unittest
from bao import *

class TestSpiel(unittest.TestCase):
    
    def setUp(self):
        self.spieler0 = 'helena'
        self.spieler1 = 'annabelle'
        self.spiel = Spiel(self.spieler0, self.spieler1)

    def test_names_of_opponents(self):
        msg = 'Der Spielername %s ist falsch gesetzt'
        self.assert_(self.spiel.bao[0].name == self.spieler0,
                     msg % self.spieler0)
        self.assert_(self.spiel.bao[1].name == self.spieler1,
                     msg % self.spieler1)

    def test_wer_is_dran(self):
        msg = 'Der falsche Spieler ist dran'
        self.assert_(self.spiel.turn == self.spiel.player.index(self.spieler0),
                     msg)
        spieler = self.spieler1
        self.spiel.dran(spieler)
        self.assert_(self.spiel.turn == self.spiel.player.index(spieler), msg)

#   zerlege ---------------------------------------------------
    def test_zerlege_richtig(self):
        for R in ('+','-'):
            for I in range(15):
                s = '%s%d' % (R,I)
                i,r = self.spiel.zerlege(s)
                self.assert_((i,r) == (I,R),
                             "%s falsch zerlegt (%s)" % (s,(i,r)))

def run_test(name):
    suite = unittest.TestSuite()
    suite.addTest(name)
    unittest.TextTestRunner(verbosity=2).run(suite)

def run_suite(name):
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSpiel)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
##    run_test(TestSpiel('test_names_of_opponents'))
    run_suite(TestSpiel)
