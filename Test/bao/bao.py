#!/usr/bin/python
# -*- coding: utf-8 -*-
"""was macht das script"""

__TODO__="""Liste der TODOs:
----------------
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
    """Ein Loch eines Bao-Brettes."""
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
        self.image = ''
        self.klammer = ('(', ')')

    def empty(self,):
        self.zahl = 0

    def add(self, n=1):
        self.zahl += n

    def mark(self,):
        self.klammer = ('[', ']')
        
    def show(self, img='', special=''):
        # TODO    schoenerer Name wuenschenswert
        """Record a string that will be shown instead of standard count pattern.
This might serve developping or debugging purposes, forinstance.
"""
        special_imgs = {'index':'%2d ' % self.index,
                        }
        img = special_imgs.get(special, img)
        if img:
            self.image = img
    
    def __str__(self,):
        kl,kr = self.klammer
        self.klammer = ('(', ')')
        if self.image:
            img = '%s%s%s ' % (kl,self.image,kr)
            self.image = ''
        else:
            img = '%s%s%s ' % (kl,self.muster.get(self.zahl,' * '),kr)
        return img

mvup = lambda x,n: x + n
mvdown = lambda x,n: x - n
        
class Bao:
    """Eine Hälfte eines Bao-Spiels. 16 Löcher. Gehört einem Spieler."""
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
        """Hält den Index auf der Schleife von 0 bis 15."""
        if index > 15:
            return index - 16
        elif index < 0:
            return index + 16
        return index

    def primitiv(self, index, richtung):
        start = self.loch(index)
        idx,count = self.get_infos(start)
        start.mark()
        start.empty()
        for i in range(1,count+1):
             neu_idx = self.periodic(richtung(index,i))
             self.loch(neu_idx).add()
        self.loch(neu_idx).mark()
        print neu_idx

    def zug(self, loch, richtung):
        """Führt einen Zug aus. Ein Zug besteht aus einer Abfolge von Primitiven.
'+' ist im Uhrzeigersinn,
'-' ist im Gegenuhrzeigersinn."""
        print self.name, loch, richtung
        self.primitiv(loch, {'+':mvup,'-':mvdown}[richtung])

    def show(self, img='', special=''):
        for i in self.board:
            i.show(img, special)

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
    """Das komplette Brett, bestehend aus 32 Löchern."""
    def __init__(self, player1, player2):
        self.player = [player1, player2]
        self.bao = [Bao(self.player[p],p) for p in (0,1)]
        self.turn = 0

    def zug(self, loch, richtung):
        self.bao[self.turn].zug(loch, richtung)
        self.turn = 1 - self.turn

    def dran(self, player):
        self.turn = self.player.index(player)

    def show(self, img='', special=''):
        self.bao[0].show(img, special)
        self.bao[1].show(img, special)
        
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
    spiel.zug(1,'-')
    print spiel
    print
    spiel.show(img=' + ', special='index')
    print spiel
