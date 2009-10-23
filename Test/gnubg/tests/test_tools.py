#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
u"""Kleine Helferfunktionen für die Tests"""

import sys
import os
import inspect
import unittest
sys.path.append(os.path.dirname(os.getcwd()))
import control

verbosity = 2

def talk(msg):
    print msg
    
def test_configuration():
    kw = {'fibs_root':'',
          'archives_root':'',
          'user':'sorrytigger'}
    return kw

class TestConfiguration(unittest.TestCase):
    """Configuration test is added to every test or testsuite"""

    def setUp(self):
        self.config = control.Config(**test_configuration())
        
    def testconfiguration(self):
        ratings = self.config.get('ratings')
        self.assert_(len(ratings) == 337, 'ratings haben falsche Länge')

def list_suites(globs):
    sts = [e for e in globs if inspect.isclass(globs[e])]
    sts = [globs[e] for e in sts \
           if globs[e].__module__ == '__main__' \
           and globs[e].__name__.startswith('Test')]
    return sts

_sum_text = {True:'ok', False:'NO'}

def sum_up_test(results):
    print '*'*70
    print 'Summary of Tests'
    print '*'*70
    for name,rc in results:
        nerr = len(rc.failures) +  len(rc.errors)
        val1 = _sum_text[rc.wasSuccessful()]
        val2 = {True:'', False:', %d errors' % nerr}[rc.wasSuccessful()]
        print "%s - %s: %d tests%s" % (val1,name,rc.testsRun,val2)
    
def run_suites(globs):
    suites = []
    for c in [TestConfiguration] + list_suites(globs):
        suites.append((c.__name__, unittest.makeSuite(c)))
    rc = []
    for c,suite in suites:
        rc.append((c,unittest.TextTestRunner(verbosity=0).run(suite)))
    sum_up_test(rc)

def run_test(name):
    suite = unittest.TestSuite()
    suite.addTest(TestConfiguration('testconfiguration'))
    suite.addTest(name)
    unittest.TextTestRunner(verbosity=2).run(suite)
