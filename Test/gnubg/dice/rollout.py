#!/usr/bin/python
# -*- coding: utf-8 -*-
"""was macht das script"""

import sys
from optparse import OptionParser
from StringIO import StringIO
import random
import pdb

dice = random.randint

def wurf():
    return (dice(1,6),dice(1,6))

class Statistics:
    def __init__(self,):
        self._sum = 0
        self._n = 0

    def mean(self,):
        if self._n > 0:
            return self._sum/float(self._n)
        else:
            return 'nan'

    def __add__(self, value):
        self._sum += value
        self._n += 1
        return self

    def __str__(self,):
        out = StringIO()
        print >> out, 'length, #, mean', self._sum, self._n, self.mean(),
        return out.getvalue()

class Race:
    def __init__(self, pips):
        self.pips = pips
        self.stats = Statistics()

    def turn(self,):
        w = wurf()
        m,n = w
        r = m + n
        if m == n:
            r *= 2
        self.pips -= r
##        print self.pips, self.stats
##        pdb.set_trace()
        self.stats += r
##        print w, self.pips
    
def usage(progname):
    usg = """usage: %s <...>
  %s""" % (progname,__doc__)
    parser = OptionParser(usg)
    parser.add_option("-l", "--leading",
                  action="store", dest="lead", type="int", default=60,
                  help="set pips of leading runner")
    parser.add_option("-t", "--trailing",
                  action="store", dest="trail", type="int", default=61,
                  help="set pips of trailing runner")
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    lead = options.lead
    trail = options.trail
    if options.verbose:
        print options,args
        print 'leading: %d   trailing: %d' % (lead,trail)
    s = 0
    for j in range(1000):
        leader = Race(lead)
        trailer = Race(trail)
        for i in range(20):
            trailer.turn()
            if trailer.pips <= 0:
                s += 1
                break
            leader.turn()
            if leader.pips <= 0:
                break
    print 'leading: %d   trailing: %d' % (lead,trail)
    print 'trailer won %d/%d times' % (s,1000)
    print 'trailer:', trailer.stats
    print 'leader: ', leader.stats
        
