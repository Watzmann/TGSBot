#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Implementierung des 'Steinspiels' Bao."""

__TODO__="""Liste der TODOs:
----------------
x. Zulassen, dass von außen die Darstellung einzelner Löcher reguliert wird.
   Die Löcher nehmen dann diese Darstellung, statt dem zahlenmäßigen Inhalt.
   Diese Darstellung gilt nur für einen Ausdruck.
2. Zug-Kriterien:
   a) Loch leer?
   b) Gegenüber mitnehmen.
"""

import sys
from optparse import OptionParser
from singleton import Singleton

class MyConfig(Singleton):

    def get_config(self,):
        return getattr(self, 'options')

    def get_config_key(self, key, default=None):
        return getattr(getattr(self, 'options'), key, default)

    def set_config(self, options):
        setattr(self, 'options', options)

class Loch:
    """Ein Loch eines Bao-Brettes."""

    klammer_standard = ('(', ')')
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
        self.front = index < 8   # True heisst "vorne", False heisst "hinten"
        self.image = ''
        self.klammer = Loch.klammer_standard

    def stop(self,):
        return self.zahl < 2    # Ein Stein wurde bereits hineingeworfen
                                # (der letzte Stein)
    def empty(self,):
        ret = self.zahl
        self.zahl = 0
        return ret

    def add(self, n=1):
        self.zahl += n

    def mark(self, img=('[', ']')):
        self.klammer = img
        
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
        self.klammer = Loch.klammer_standard
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
        self.config = MyConfig().get_config()
        self.verbose = self.config.verbose
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

    def spiel_gegner(self, bao):
        self.gegner = bao
        print "%s's Gegner ist %s" % (self.name, self.gegner.name)

    def loch(self, index):
        loch = self.board[self.index[index]]
        return loch

    def periodic(self, index):
        """Hält den Index auf der Schleife von 0 bis 15."""
        if index > 15:
            return index - 16
        elif index < 0:
            return index + 16
        return index

    def voranschreiten(self, index, richtung, count):
        for i in range(1,count+1):
            idx = self.periodic(richtung(index,i))
            loch = self.loch(idx)
            loch.add()
        beute = self.check_opposite(loch)
        loch.add(beute)
        if self.verbose:
            print 'beute', beute
        loch.show('.+.')
        return loch

    def primitiv(self, index, richtung):
        """Ein Primitiv-Zug von 'index' in 'richtung'.
Primitive sind rekursiv. Sie folgen einander, bis ein Stopp (leeres Loch)
erfolgt.
"""
        start = self.loch(index)
        count = start.empty()
        current = self.voranschreiten(index, richtung, count)
        current.mark(('{','}'))
        self.stop += 1
        print current.index, self.stop
        if not current.stop():
            if not (self.stop > 6):
                print 'noch mal'
                current = self.primitiv(current.index, richtung)
        return current

    def zug(self, loch, richtung):
        """Führt einen Zug aus. Ein Zug besteht aus einer Abfolge von Primitiven.
'+' ist im Uhrzeigersinn,
'-' ist im Gegenuhrzeigersinn."""
        print self.name, loch, richtung
        self.stop = 0
        self.loch(loch).show(img=' 0 ')
        self.loch(loch).mark()
        current = self.primitiv(loch, {'+':mvup,'-':mvdown}[richtung])
        current.show(img=' # ')
        current.mark()

    def check_opposite(self,loch):
        if self.verbose:
            print "ich bin auf %s's seite in loch %d" % (self.name,loch.index)
        ret = 0
        if loch.front:
            print 'gegners loch:', self.gegner.index[loch.index+8]
            ret = self.gegner.loch(self.gegner.index[loch.index+8]).empty()
        return ret
    
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
        self.bao[0].spiel_gegner(self.bao[1])
        self.bao[1].spiel_gegner(self.bao[0])
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

    MyConfig().set_config(options)
        
    spiel = Spiel('helena','annabelle')
##    spiel.dran('andreas')
    print spiel
    spiel.zug(14,'+')
    print spiel
    spiel.zug(1,'-')
    print spiel
    print
    spiel.show(img=' + ', special='index')
    print spiel
