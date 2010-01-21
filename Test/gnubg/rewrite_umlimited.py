#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""Konvertiert die JavaFibs Match-Datei (.match) von unlimited-Matches.
Die konvertierte Datei kann in jellyfish-Format umgewandelt werden und ist
für gnubg lesbar."""

import sys
import os
from optparse import OptionParser

def score(result, s):
            a = s.split(':')
            if a[1] == 'You':
                result[1] += int(a[2])
            else:
                result[0] += int(a[2])

def get_final_result(match):
    result = [0,0]  # opponent:you
    for m in match:
        if m.startswith('7:'):
            score(result, m)
            #print result[0],':',result[1]
    return max(result)

def get_opponent(match):
    for m in match:
        if m.startswith('8:'):
            a = m.split(':')
            opp = a[1]
            break
    return opp

def doit(filename):
    m = open(filename)
    lm = m.read().splitlines()
    result = [0,0]  # opponent:you
    you = 'sorrytigger'
    ML = get_final_result(lm)       # ML is match length
    opp = get_opponent(lm)
    for i in lm:
        if i.startswith('8:'):
            a = i.split(':')
            a[2] = str(ML+5)
            print ':'.join(a)
        elif i.startswith('7:'):
            print i
            score(result, i)
            if max(result) == ML:
                a = i.split(':')
                if a[1] == 'You':
                    win = 'You'
                    res = result[1]
                else:
                    win = opp
                    res = result[0]+5
                print '9:%s:%d' % (win,res)
                break               # stop output
            print '14:%s-%d:%s-%d' % (you,result[1],opp,result[0])
        else:
            print i
        
def usage(progname):
    usg = """usage: %s <unlimited Match>
  %s

Beispiel:
  %s /opt/JavaFIBS2001/matches/internal/TwoDice.match > TD.unlimited.match
""" % (progname,__doc__,progname)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if len(args) < 1:
        print usg
        print "!! missing pathname of unlimited match"
        sys.exit(1)
    unlimited = args[0]
    if not os.path.isfile(unlimited):
        print "!! %s cannot be found"
        sys.exit(2)
    if options.verbose:
        print 'converting', unlimited

    doit(unlimited)

