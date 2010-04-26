#!/usr/bin/python
# -*- coding: utf-8 -*-
"""was macht das script"""

__TODO__="""Liste der TODOs:
-----------------
1. Zulassen, dass von außen die Darstellung einzelner Löcher reguliert wird.
   Die Löcher nehmen dann diese Darstellung, statt dem zahlenmäßigen Inhalt.
   Diese Darstellung gilt nur für einen Ausdruck.
2. Zug-Kriterien:
   a) Loch leer?
   b) Gegenüber mitnehmen.
"""

import sys
from optparse import OptionParser

class Loch:
    muster = {
        0:'   ',
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

    def empty(self,):
        self.zahl = 0

    def add(self, n=1):
        self.zahl += n

    def __str__(self,):
        return '(%s) ' % self.muster.get(self.zahl,' * ')
##        return '(%2d ) ' % self.index

mvup = lambda x,n: x + n
mvdown = lambda x,n: x - n
        
class Bao:
    def __init__(self, name, darstellung=0):
        self.name = name
        self.darstellung = darstellung
        self.start_aufstellung()
##        print name, 'initialisiert'
        
    def start_aufstellung(self,):
        p1 = range(8)
        p2 = [p+8 for p in p1]
        p1.reverse()
        aufstellung = p1 + p2
        self.index = aufstellung
        if self.darstellung == 1:
            aufstellung.reverse()
            self.index = p2 + p1
        self.board = [Loch(i) for i in aufstellung]
        print self.name
        print self.index

    def loch(self, index):
        loch = self.board[self.index[index]]
        return loch

    def get_infos(self, loch):
        return loch.index, loch.zahl

    def periodic(self, index):
        if index > 15:
            return index - 16
        elif index < 0:
            return index + 16
        return index

    def primitiv(self, index, richtung):
        start = self.loch(index)
        idx,count = self.get_infos(start)
        start.empty()
        for i in range(1,count+1):
             neu_idx = self.periodic(richtung(index,i))
             self.loch(neu_idx).add()
        print neu_idx

    def zug(self, loch, richtung):
        """Führt einen Zug aus. Ein Zug besteht aus einer Abfolge von Primitiven.
'+' ist im Uhrzeigersinn,
'-' ist im Gegenuhrzeigersinn."""
        print self.name, loch, richtung
        self.primitiv(loch, {'+':mvup,'-':mvdown}[richtung])

    def __str__(self,):
        s = ''.join([str(i) for i in self.board])
        name1 = name2 = ''
        if self.darstellung == 0:
            name1 = ' ' + self.name
        else:
            name2 = ' ' + self.name
        s = s[48:] + name1 + '\n' + s[:48] + name2
        return s

class Spiel:
    def __init__(self, player1, player2):
        self.player = [player1, player2]
        self.bao = [Bao(self.player[p],p) for p in (0,1)]
        self.turn = 0

    def zug(self, loch, richtung):
        self.bao[self.turn].zug(loch, richtung)
        self.turn = 1 - self.turn

    def dran(self, player):
        self.turn = self.player.index(player)

    def __str__(self,):
        b1 = self.bao[0].__str__()
        b2 = self.bao[1].__str__()
        return b1 + '\n' + '-'*48 + '\n' + b2
        
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
        print __TODO__

    spiel = Spiel('helena','andreas')
##    spiel.dran('andreas')
    print spiel
    spiel.zug(14,'+')
    print spiel
    spiel.zug(0,'-')
    print spiel
