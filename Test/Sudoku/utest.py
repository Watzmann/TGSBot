#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Unittests fuer Sudoku.

Suites:
    SpieleSuite:    Spiele werden auf Konsistenz geprüft (spiele.py).
    MethodenSuite:  Methoden (stamp und lines) werden getestet (sudoku.py).
"""

import sys
import unittest
from sudoku import *

class Options:
    def __init__(self,):
        self.verbose = False
        self.debug = False
        self.quiet = True
    def __str__(self,):
        return str(self.__dict__)

class TestSpieleKonsistenz(unittest.TestCase):

    def __init__(self,spiel):
        self.spiel = spiel
        unittest.TestCase.__init__(self)
            
    def setUp(self):
        name,test = self.spiel
        self.game = Sudoku(test,name,Options())

    def runTest(self):
        res = self.game.check()
        self.assert_(res, '%s inkonsistent' % self.game.name)

class SpieleSuite(unittest.TestSuite):

    def __init__(self):
        unittest.TestSuite.__init__(self,map(TestSpieleKonsistenz,
                                             map(testfall,test_faelle.keys())))


##def test_is_aligned():
##    """Testet einige Konstellationen von 2er- und 3er-Tupeln auf Alignment.
##
##DIES GEHOERT IN EINEN UNITTEST TESTCASE!
##
##Getestet wird die Funktion Sudoku.is_aligned().
##Es werden einige gute Konstellationen aufgebaut und nicht geprueft.
##Es werden einige gute und schlechte Konstellationen aufgebaut und gegen die
##eben erzeugten guten geprueft. Das Testergebnis wird in jedem Falle ausgegeben.
##"""
##    n,t = testfall()
##
##    S=Sudoku(t,n,options=options)
##    s=S.stamps[0]
##
##    good_rows = build_line(([0,1,2],[3,4,5],[6,7,8]))
##    good_cols = build_line(([0,3,6],[1,4,7],[2,5,8]))
##    bad_rows = build_line(([1,3,6],[1,2,7],[2,5,7]))
##
##    check = {}
##    for f in (good_rows,good_cols,):
##        for i in f:
##            ss = s.is_aligned(i)
##            check[tuple(i)] = ss
##
##    print '-'*40
##    for f in (bad_rows,):
##        for i in f:
##            ss = s.is_aligned(i)
##            if ss:
##                ok = ss == check[tuple(i)]
##            else:
##                ok = not check.has_key(tuple(i))
##            print i,ss,'\t\t',ok


if __name__ == "__main__":
    v = 1
    if len(sys.argv) > 1:
        v = int(sys.argv[1])
    suite = SpieleSuite()
    unittest.TextTestRunner(verbosity=v).run(suite)


