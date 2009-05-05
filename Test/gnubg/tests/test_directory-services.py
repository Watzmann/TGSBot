#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
u"""Testet die Directory-Services von control.py"""

import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))
import unittest
import control
from mgnubg import Gnubg
from test_tools import *

class TestConfig(unittest.TestCase):
    
    def setUp(self):
        self.config = control.Config(**test_configuration())

    def testconfig(self):
        correct = self.config.settings_correct()
        self.assert_(correct,'Fehler in Config()')

class TestDirectoryServices(unittest.TestCase):
    
    def setUp(self):
        self.config = control.Config(**test_configuration())
        self.kdb = control.Information(self.config)

##    def tearDown(self):

    def testnotconverted(self):
        # make sure not converted matches are found
        it = self.kdb.internal_matches
        jm = self.kdb.jellyfish_matches
        uc = []
        for i in it.pliste:
            km = i.match_id
            if not jm.dliste.has_key(km):
                uc.append(km)
        self.assert_(len(uc) == 2,"Falsche Zahl von 'unkonvertierten' Matches")
        self.assert_('You_vs_anke_1225750135619' in uc,
                     "'Unkonvertiertes' Match nicht entdeckt")

    def testpurge(self):
        # make sure 2 incomplete matches are removed from Matches
        # original count is 6 Matches
        jlen = 6
        jm = self.kdb.jellyfish_matches
        self.assert_(len(jm) == jlen,'Länge vor purge() nicht korrekt')
        purged = jm.purge()
        plen = len(purged)
        self.assert_(len(jm) == (jlen - plen),'Länge nach purge() nicht korrekt')
        len_dliste_old = len(jm.dliste)
        jm.list2hash()
        new_len = len_dliste_old - len(jm.dliste)
        self.assert_(new_len == plen,'Länge nach rehash nicht korrekt')

    def testrenametimestamp(self):
        # make sure, proper matches are processed and rename takes place
        kdb = self.kdb
        kdb.purge_matches()
        jms = kdb.rename_time_stamp(Gnubg())
        soll = ['#',]
        self.assert_(jms == soll,'ist,soll\n%s\n%s'%(jms,soll))

    def testotheruser(self):
        pass
    def testarchive(self):
        pass # siehe check_matches
    def testdelete(self):
        pass # siehe test_matches
    def testrenameopponent(self):
        pass

class TestElementaryActions(unittest.TestCase):
    
    def setUp(self):
        self.config = control.Config(**test_configuration())
        self.kdb = control.Information(self.config)

    def testfile_ignored(self):
        # make sure matches/internal/any_not_match_file not in Matches
        self.assert_(len(self.kdb.internal_matches.liste) == 8)
        match_id = 'any_not_match_file'
        self.assert_(not match_id in self.kdb.internal_matches.dliste)

    def testmatch_in_list(self):
        # make sure match is in Matches
        match_id = 'You_vs_agenorltd_1224621584972'
        self.assert_(match_id in self.kdb.internal_matches.dliste)
        self.assert_(match_id in self.kdb.jellyfish_matches.dliste)

    def testmatch_not_in_list(self):
        # make sure match is not in Matches
        match_id = 'You_vs_agenorltd_1004621584972'
        self.assert_(not match_id in self.kdb.internal_matches.dliste)
        self.assert_(not match_id in self.kdb.jellyfish_matches.dliste)

    def testmatch_complete(self):
        # make sure match is complete
        match_id = 'You_vs_deltaics_1219658568376'
        match = self.kdb.jellyfish_matches.dliste[match_id]
        self.assert_(match.is_complete())

    def testmatch_not_complete(self):
        # make sure match is not complete
        match_id = 'You_vs_zig_1225558377684'
        match = self.kdb.jellyfish_matches.dliste[match_id]
        self.assert_(not match.is_complete())

if __name__ == "__main__":
    print control.Config(**test_configuration())
    do_suites = (len(sys.argv) > 1) and (sys.argv[1] == 'suites')

    verbosity = 2
    if not do_suites:
        run_test(TestDirectoryServices('testrenametimestamp'))
    else:
        run_suites(globals())
