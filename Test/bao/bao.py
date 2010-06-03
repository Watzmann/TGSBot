#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Implementierung des 'Steinspiels' Bao."""

__TODO__="""Liste der TODOs:
----------------
3. Unittests.
4a.  Falsche Eingaben von Zügen checken und Massnahmen ergreifen.
5. Debug-Version von einem Zug, wobei jedes Primitiv verfolgt wird.
6. Pruefen, dass man nur aus einem Loch startet, wenn dort >2 ist.
7. Strategie 1): Zug mit den meisten Beute-Steinen finden.
8. Strategie 2): Zug mit der niedrigsten (eigenen) Front-Zahl finden.
9. Strategie 3): Zug mit der höchsten (gegn.) Zahl leerer Frontlöcher.
"""
__DONE__="""Erledigte TODOs:
----------------
1. Zulassen, dass von außen die Darstellung einzelner Löcher reguliert wird.
   Die Löcher nehmen dann diese Darstellung, statt dem zahlenmäßigen Inhalt.
   Diese Darstellung gilt nur für einen Ausdruck.
2. Zug-Kriterien:
   a) Loch leer?
   b) Gegenüber mitnehmen.
4. Zugabfolge mit Eingabe von start,richtung von der Console.
"""

import sys
import StringIO
from optparse import OptionParser
import copy
#from singleton import Singleton

QUIET = __name__ != '__main__'

def talk(msg):
    if not QUIET and 'options' in globals():
        if options.verbose:
            print msg

def dbg(msg):
    if not QUIET and 'options' in globals():
        if options.debug:
            print msg

class Strategy:
    """Strategy ermittelt den besten Zug nach einer Reihe von Kriterien."""

    def __init__(self, spiel):
        self.spiel = spiel
        self.zuege = {}
        for z in self.zugliste('+'):
            print z
            test = copy.deepcopy(spiel)
            test.zug(z[1],z[0])
            self.zuege[z[2]] = test

    def zugliste(self,c):
        return ((c,i,'%s%s' % (c,i)) for i in range(16))

    def __str__(self,):
        output = StringIO.StringIO()
        for k in self.zuege:
            print >>output, k
            print >>output, self.zuege[k]
            print >>output, '='*60
        return output.getvalue()
        
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
LINE = '-'*48
        
class Bao:
    """Eine Hälfte eines Bao-Spiels. 16 Löcher. Gehört einem Spieler."""
    def __init__(self, name, darstellung=0, debug=False, spiel=None):
        self.name = name
        self.darstellung = darstellung
        self.start_aufstellung()
        self.debug = debug
        self.spiel = spiel
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
        dbg(str(self.name))
        dbg(str(self.index))

    def spiel_gegner(self, bao):
        self.gegner = bao
        dbg("%s's Gegner ist %s" % (self.name, self.gegner.name))

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
        self.debug_info = (loch.zahl, beute)
        loch.add(beute)
        talk('beute %s' % beute)
##        loch.show('.+.')
        return loch

    def primitiv(self, index, richtung):
        """Ein Primitiv-Zug von 'index' in 'richtung'.
Primitive sind rekursiv. Sie folgen einander, bis ein Stopp (leeres Loch)
erfolgt.
"""
        start = self.loch(index)
        count = start.empty()
        if count > 1:       # TODO:
                            # Diese Stelle gefällt mir nicht, weil
                            # sie quasi die current.stop-Abfrage darstellt;
                            # kann man nicht hier schon nach current.stop
                            # fragen??
            current = self.voranschreiten(index, richtung, count)
            if self.debug:
                print
                self.spiel.show(img=' + ', special='index')
                print self.spiel
                print
                start.mark()
                current.mark(('{','}'))
    ##        print current.index, self.stop
            if not current.stop():
                if self.debug:
                    print self.spiel
                    info = (current.index,) + self.debug_info + (current.zahl,)
                    raw_input('Loch %d   %d+%d=%d (Enter) ' % info)
                current = self.primitiv(current.index, richtung)
        return current

    def zug(self, loch, richtung):
        """Führt einen Zug aus. Ein Zug besteht aus einer Abfolge von Primitiven.
'+' ist im Uhrzeigersinn,
'-' ist im Gegenuhrzeigersinn."""
        dbg("%s %s %s" % (self.name, loch, richtung))
        if self.debug:
            self.loch(loch).show(img=' 0 ')
            self.loch(loch).mark()
        current = self.primitiv(loch, {'+':mvup,'-':mvdown}[richtung])
##        current.show(img=' # ')
##        current.mark()

    def check_opposite(self,loch):
        talk("ich bin auf %s's seite in loch %d" % (self.name,loch.index))
        ret = 0
        if loch.front and loch.zahl > 1:
            gegner_idx = 7 - loch.index
            dbg('gegners loch: %d' % gegner_idx)
            ret = self.gegner.loch(gegner_idx).empty()
        return ret
    
    def strategy(self,):
        return self.spiel.strategy()

    def show(self, img='', special=''):
        for i in self.board:
            i.show(img, special)
            
    def print_mit_scharnier(self,):
        s = self.__str__()
        if self.darstellung == 0:
            s = s + '\n' + LINE
        else:
            s = LINE + '\n' + s
        return s
        
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
    def __init__(self, player1, player2, debug=False):
        self.player = [player1, player2]
        self.bao = [Bao(self.player[p],p,debug=debug,spiel=self) for p in (0,1)]
        self.bao[0].spiel_gegner(self.bao[1])
        self.bao[1].spiel_gegner(self.bao[0])
        self.turn = 0
        self.ende = False

    def zug(self, loch, richtung):
        self.bao[self.turn].zug(loch, richtung)
        self.turn = 1 - self.turn

    def spielen(self, start_spieler=''):
        if start_spieler == '':
            start_spieler = self.player[self.turn]
        self.dran(start_spieler)
##        self.zug(14,'+')
##        print
##        print self
        while not self.ende:
            spieler = self.player[self.turn]
            print
            self.bao[self.turn].show(img=' + ', special='index')
            print self.bao[self.turn].print_mit_scharnier()
            eingabe = raw_input('%s, bitte einen Zug eingeben (z.B. +14, -6): ' % spieler)
            i,r = self.zerlege(str(eingabe))
            print i,r
            self.zug(i,r)
            print
            print self
  
    def zerlege(self, eingabe):
##        print eingabe, type(eingabe)
        r = eingabe[0]
        s = int(eingabe[1:])
        return s,r

    def dran(self, player=''):
##        print 'dran  vorher', self.turn, self.player[self.turn]
        if player == '':
            self.turn = 1 - self.turn
        else:
            self.turn = self.player.index(player)
##        print 'dran nachher', self.turn, self.player[self.turn]
        return self.player[self.turn]

    def strategy(self,):
        strategy = Strategy(self)
        return str(strategy)

    def show(self, img='', special=''):
        self.bao[0].show(img, special)
        self.bao[1].show(img, special)
        
    def __str__(self,):
        b1 = self.bao[0].__str__()
        b2 = self.bao[1].__str__()
        return b1 + '\n' + LINE + '\n' + b2
        
def usage(progname):
    usg = """usage: %s <...>
  %s""" % (progname,__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    parser.add_option("-d", "--debug",
                  action="store_true", dest="debug", default=False,
                  help="print debugging information to stdout")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args
        print __TODO__

    spiel = Spiel('helena','andreas',debug=options.debug)
    print spiel
##    spiel.zug(14,'+')
##    print spiel
##    print
##    print spiel
##    spiel.zug(1,'-')
##    print spiel
##    print
##    print spiel
##    print
##    spiel.show(img=' + ', special='index')
##    print spiel
    print '='*60
    print spiel.strategy()
#    spiel.spielen()
