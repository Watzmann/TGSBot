#!/usr/bin/python
# -*- coding: utf-8 -*-
"""was macht das script"""

import sys
from optparse import OptionParser
from StringIO import StringIO

BASIC = range(1,7)
SINGLEROLL = 0
SINGLEMEAN = 1

class Statistics:
    def __init__(self, frequencies, vector=0):
        self.frequencies = frequencies
        self.summe = float(sum(frequencies))
        self.freq = [l/self.summe for l in frequencies]
        if vector != 0:
            s = zip(frequencies, vector)
            self.mean = sum([a*b for a,b in s])/self.summe

    def __str__(self,):
        out = StringIO()
        print >> out, self.summe
        return out.getvalue()
    
class Frequency:
    def __init__(self, dice):
        self.dice = dice
        h = {}
        for a in dice:
            for a0 in a[1]:
                v = h.get(a0,0)
                h[a0] = v + 1
        k = h.keys()
        k.sort()
        self.values = k
        self.freq = [h[l] for l in k]
        self.stats = Statistics(self.freq, self.values)

    def __str__(self,):
        out = StringIO()
        print >> out, self.values, len(self.values)
        print >> out, self.freq, sum(self.freq)
##        print >> out, self.stats.freq, sum(self.stats.freq)
        factor = {True:self.stats.mean/SINGLEMEAN, False:''}[SINGLEMEAN!=1]
        print >> out, self.stats.mean, factor
        return out.getvalue()

class Dice():
    def __init__(self, length, clip=-1):
        a = []
        _length = length
        if clip > 0:
            for e,i in enumerate(length):
                if i >= clip:
                    break
            _length = length[:e]
        sr = SINGLEROLL
        if sr == 0:
            sr = _length
        for i in sr:
            a.append([i,[i+n for n in _length]])
            if _length == BASIC:
                a[-1][1][i-1] *= 2
        self.rolls = a
        self.frequency = Frequency(a)

    def vorsprung(self, trailing, leading):
        """Berechnet für einen Würfelsatz die Wahrscheinlichkeit, dass
der trailing player einen Vorsprung erwürfelt.
trailing ist die benötigte Augenzahl des nachhängenden Spielers,
leading die des führenden."""
        trail = -1
        for e,i in enumerate(self.frequency.values):
            if i < leading:
                lead = e
            if i >= trailing:
                trail = e
                break
        if lead == len(self.frequency.values)-1 and \
           self.frequency.values[-1] < leading:
            lead = -1
        #print lead, trail
        p_vorsprung = .0
        if trail > -1:
            p_trail = self.frequency.values[trail]
            p_lead = self.frequency.values[lead]
            #print p_lead, p_trail
            p_trail = sum(self.frequency.stats.freq[trail:])
            p_lead = sum(self.frequency.stats.freq[:lead+1])
            p_vorsprung = p_trail * p_lead
            #print p_lead, p_trail, p_vorsprung
        return p_vorsprung

    def __str__(self,):
        out = StringIO()
        for a in self.rolls:
            print >> out, a
        return out.getvalue()

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

    dice = Dice(BASIC)
    SINGLEROLL = dice.frequency.values
    SINGLEMEAN = dice.frequency.stats.mean
    di = []
    vorsprung = .0
##    lead = 60
##    trail = 61
    for d in range(5):
        #print dice.frequency
        vorsprung += dice.vorsprung(trail,lead)
        di.append(dice)
        dice = Dice(dice.frequency.values, clip=trail)
    #print dice.frequency
    vorsprung += dice.vorsprung(trail,lead)
    print 'Wahrscheinlichkeit für', trail,lead,'ist', vorsprung
