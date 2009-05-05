#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
u"""liest die Shelve-Datenbank <DB> aus.
    Mit 'verbose' lassen sich die Datensätze ausgeben.

    DB:     Name der Datenbank [dbshelve]"""
# 

import shelve
import sys
from optparse import OptionParser
from mgnubg import Match, Summary
import eval_db

def detailed_print(data, key):
    summary = load_summary(key)
##    print 'detail::',key
##    print 'detail::',summary.data['info']
    smry = summary.compose_summary()
    if options.values:
        vals = options.values.split(',')
        for v in vals:
            print eval_db.sorting_functions[v][0](smry),
        print key
    else:
        if options.sorting:
            val = eval_db.sorting_functions[options.sorting][0](smry)[0]
        else:
            val = ''
        print '*'*20, val, key
    if options.match_info:
        print summary.str_info()
    if options.verbose:
        d = data[key]
        for k in d:
            print '+'*20, k
            print d[k]
    if options.analysis:
        print summary.str_info()
        print '='*90
        for g in smry['games']:
            print summary.str_analysis(g)
            print '-'*90
        print '='*90
        print summary.str_analysis(smry['match'])

def load_summary(key):
    match = Match(match_id=key)
    return match.summary

def usage(progname):
    usg = """usage: %prog <DB>
  %prog """ + __doc__
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    parser.add_option("-k", "--key",
                  action="store", type="string", dest="key",
                  help="print this key only")
    parser.add_option("-g", "--grep-key",
                  action="store", type="string", dest="grep",
                  help="print keys containing this pattern")
    parser.add_option("-s", "--sort",
                  action="store", type="string", dest="sorting",
                  help="sort for key")
    parser.add_option("-V", "--values",
                  action="store", type="string", dest="values",
                  help="show tuple of values (comma separated list of time,rating,...)")
    parser.add_option("-a", "--analysis",
                  action="store_true", dest="analysis", default=False,
                  help="print analysis")
    parser.add_option("-i", "--info",
                  action="store_true", dest="match_info", default=False,
                  help="print match info")
    parser.add_option("-G", "--games",
                  action="store_true", dest="games", default=False,
                  help="consider games rather than matches")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args
    if len(args) > 0:
        filename = args[0]
    else:
        filename = 'gnubg.db'

    d = shelve.open(filename) # open -- file may get suffix added by low-level
                              # library

    klist = d.keys() # a list of all existing keys (slow!)
##    klist = klist[:20]
    if options.sorting:
        klist = eval_db.sort_liste(klist,options.sorting,games=options.games)
    if options.key:
        detailed_print(d,options.key)
    elif options.grep:
        for k in klist:
            if k.find(options.grep) > -1:
                detailed_print(d,k)                
    else:
        for k in klist:
            detailed_print(d,k)

    d.close()       # close it
