#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
u"""verarbeitet BG-Matches zu Statistiken"""

import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))
import unittest
import control
from test_tools import *

class TestMatches(unittest.TestCase):
    
    def setUp(self):
        self.config = control.Config(**test_configuration())
        self.matches = self.config.get('matches')

    def testnr_of_entries(self):
        self.assert_(len(self.matches) == 128)

    def test_repr_(self):
        self.assert_(self.matches.__repr__() == \
                     '128 entries in user/sorrytigger/matches',
                     'representation of matches has changed')

    def testaverages(self):
        # make sure averages are calculated correctly
        spans = (3,5,10,20,50,100,128)
        sums = [2,3,6,12,29,61,71]
        deltas = [i+'./...' for i in ['  8.96','  3.68','  3.84',
                                      '  4.20','  3.25',' 19.75',]] + ['',]
        avgs = [float(s)/p for p,s in zip(spans,sums)]
        soll = zip(spans,avgs,deltas)
        avg = self.matches.get_averages()
        self.assert_(avg == soll,'avg,soll\n%s\n%s'%(avg,soll))

    def testgliding_averages(self):
        # make sure gliding_averages are calculated correctly
        # make sure correct number of lines is issued
        soll = {        # only the following lines are tested
            0:  'Datum;;3;5;10;20;50;100;128',
            2:  '09.02.08;1202553384857;0,0000;0,0000;0,2000;0,3000;0,3704',
            10: '17.02.08;1203255984744;0,3333;0,4000;0,4000;0,3500;0,4000',
            37: '02.03.08;1204472729599;0,3333;0,4000;0,5000;0,6000;0,5200;0,5161',
            91: '21.03.08;1206119508387;0,3333;0,6000;0,5000;0,5500;0,5800;0,5600;0,5431',
            }            
        self.matches.process()
        avg = self.matches.gliding_averages()
        for e,a in enumerate(avg):
            s = soll.get(e,'')
            if s != '':
                self.assert_(a == s,'avg,soll in Zeile %d\n%s\n%s'%(e,a,s))
        self.assert_(e == 103,'Falsche Zahl von Ausgabezeilen (%d)'%e)

class TestRatings(unittest.TestCase):
    
    def setUp(self):
        self.config = control.Config(**test_configuration())
        self.matches = self.config.get('matches')
        self.ratings = self.config.get('ratings')

    def testnr_of_entries(self):
        self.assert_(len(self.ratings) == 338)

    def testmatch_rating(self):
        # make sure rating is found correctly
        rating = self.ratings.match_rating(1206345788892,)
        self.assert_(long(rating.experience) == 383)

    def testmatch_rating_delta(self):
        # make sure rating-delta is calculated correctly
        rating,delta = self.ratings.match_rating(1206345788892,delta=True)
        adelta = (1520.66-1523.00)
        self.assert_(delta == adelta,'%f == %f'%(adelta,delta))

if __name__ == "__main__":
    print control.Config(**test_configuration())  # TODO: das hier auch als Test
                                # Config nicht drucken
                                # einzelne Elemente mit assert
                                # in den test_tools
    do_suites = (len(sys.argv) > 1) and (sys.argv[1] == 'suites')

    if not do_suites:
        run_test(TestMatches('testgliding_averages'))
    else:
        run_suites(globals())
