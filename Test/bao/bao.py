#!/usr/bin/python
# -*- coding: utf-8 -*-
"""was macht das script"""

import sys
from optparse import OptionParser

class Loch:
    muster = {
        1:' . ',
        2:' : ',
        3:'...',
        4:'.:.',
        5:':.:',
        6:':::',
        }
    def __init__(self, index):
        self.zahl = 2
        self.index = index
        self.type = index < 8   # True heisst "vorne", False heisst "hinten"

    def __str__(self,):
        return '(%s) ' % self.muster.get(self.zahl,' * ')
        
class Bao:
    def __init__(self, name, darstellung=0):
        self.name = name
        self.start_aufstellung()
        self.darstellung = darstellung
        print name, 'initialisiert'
        
    def start_aufstellung(self,):
        self.board = (Loch(i) for i in range(16))

    def __str__(self,):
        s = ''.join([str(i) for i in self.board])
        name1 = name2 = ''
        if self.darstellung == 0:
            name1 = ' ' + self.name
        else:
            name2 = ' ' + self.name
        s = s[48:] + name1 + '\n' + s[:48] + name2
        return s

def usage(progname):
    usg = """usage: %s <...>
  %s""" % (progname,__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args
    bao1 = Bao('helena', 0)
    bao2 = Bao('andreas', 1)
    print bao1
    print '-'*48
    print bao2
    
