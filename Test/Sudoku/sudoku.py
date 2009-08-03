#!/usr/bin/python
# -*- coding: utf-8 -*-
"""was macht das script"""

import sys
from optparse import OptionParser
from Tkinter import *
from random import randint
from StringIO import StringIO

from tkSudo import sudokuChart
from spiele import test_faelle
from zeit_spiele import zeit_archiv

todo = """1) done-flags benutzen
2) Alarm bei Inkonsistenz in ....paint() korrekt einsetzen;
3) die 424 geht noch nicht
3a) -> Anmerkung in spiele.py @ test424
4) -> Anmerkung in Sudoku.query_done()
5) Stamp und Line zusammenführen
6) Unit_tests()
7) Paar (possible und mbn) noch nicht wirklich getestet
8) ...und: Drillinge noch mal überprüfen (s.a. http://www.sudokumania.de/tipps4.html)
10) Einzelschrittmodus in der Anzeige
11) Meldungen in der Anzeige ausgeben
12) "Fertig" -> schritt ausgrauen
"""

# Suche nach Clues:
# -----------------
#
# Quadruple:
#   Zellen auf Rechteck suchen (Quadruple); wenn von den vier Zellen auf
#   einer nur eine Möglichkeit bleibt, dann gilt diese.
#   Quatsch: weil die Ziffern sich über die Diagonale nicht beeinflussen.
#
# find_bummers:
#   Auf einer Line aus den possible eine 'Wahl' finden, die zu einer nicht
#   lösbaren Besetzung führt und diese dann ausschließen können.
#   Bummer: hat bei den getesteten Spielen nicht zu einer Lösung geführt.
#
# Quadruple:
#   Der 'find_bummers'-Ansatz nicht auf der Line, sondern auf allen möglichen
#   Quadruplen.
#   Bummer: hat bei dem getesteten Spiel 'test427' nicht zu einer Lösung
#   geführt.

def testfall(name='test427'):
    test = [t.replace('.',' ') for t in test_faelle[name]]
    return name,test

def mycycle(n):
    if ' ' == n:
        return n
    d = int(n) + 1
    if d > 9:
        d = 1
    return str(d)

class Sudoku:
    
    def __init__(self, pattern, name='', options={}):
        """pattern is a list of 9 digit strings; each string contains
digits and blanks."""
        self.name = name
        self.options = options
        if not self.options.quiet:
            print 'Sudoku',name
        self.game = tuple([self.convert_line(c) for c in pattern])
        self.dumped_list = self.list_dump()
        self.stamps = self.build_stamps()
        self.rows = self.build_rows()
        self.cols = self.build_cols()
        self.link_partners()
##        self.next_type = -1
##        self.next_nr_steps = 3
##        self.stuck = False
        return

    def convert_line(self, line):
        return tuple(line)

    def list_dump(self):
        l = []
        for i in self.game:
            l += i
        return l

    def list_load(self, liste):
        self.game = tuple([tuple(liste[9*i:9+9*i]) for i in range(9)])

    def next(self):
        cont = True
        if self.query_done():
            if not self.options.quiet:
                print 'FERTIG'
            msg = 'done'
            cont = False
        if cont:                # cont muss weg! Es muss einen Status "done,stuck" geben
            changed = 0
            cycles = 10
            while cycles:
                cycles -= 1
                for i in self.stamps:
                    changed += i.guess()
                if changed:
                    break
                for i in self.rows:
                    changed += i.guess()
                if changed:
                    break
                for i in self.cols:
                    changed += i.guess()
                if changed:
                    break
            if changed:
                self.rebuild_from_stamps()
                msg = 'stepping'
                cont = True
                self.sudoku_guess = False
            else:
                if not self.sudoku_guess:
                    hit = self.quadruple()
                    if hit:
                        self.rebuild_from_stamps()
                    self.sudoku_guess = True
                    cont = True
                    msg = 'big guess'
                else:
                    if not self.options.quiet:
                        print "STUCK: no changes"
                    msg = '-stuck-'
                    cont = False
        return cont,msg

    def excerpt(self, liste, indices):
        return [liste[i] for i in indices]

    def set_value(self, value=0, stamp=None, absolute=None):
        """Sets single value in a Sudoku.
Used for manual settings and for guesses like quadruple.
value = integer element of range(1,10) or returns with no change.
stamp = (<stamp_position>,<index in stamp>)
absolute = <absolute index>
'absolute' is converted to (<stamp_position>,<index in stamp>);
Rebuild is performed.
"""
        if value not in range(1,10):
            return
        if stamp:
            self.stamps[stamp[0]].set_hit(stamp[1], value)
        elif absolute:
            s,i = self.convert_absolute(absolute)
            if s not in range(9):
                return
            self.stamps[s].set_hit(i, value)
        self.rebuild_from_stamps()

    def convert_absolute(self, index):
        row = index / 9
        col = index % 9
        stamp = (row / 3)*3 + col / 3
        index = (row % 3)*3 + col % 3
        return (stamp,index)
    
    def quadruple(self,):
##        if self.name == 'test427':
##            self.set_value(7,stamp=(8,3),absolute=69)
        print 'in quadruple()', '-'*40
        # look for 4 corners of rectangle
        #    in these exactly 4 different candidates
        #    one of them only in one field
        #    -> this is a hit
        for h,r in enumerate(self.rows[:-1]):
            if len(r.misses) < 2:
                continue
            r.info()
            print '  possible',r.possible
            cols = r.possible.keys()
            cols.sort()
            for e,c in enumerate(cols[:-1]):
                if len(r.possible[c]) > 4:      # too many digits
                    continue
                corner0 = c
                col1 = self.cols[corner0]
                if len(col1.misses) < 2:        # too few missing
                    continue
                for corner1 in cols[e+1:]:
                    if len(r.possible[corner1]) > 4:      # too many digits
                        continue
                    col2 = self.cols[corner1]
                    if len(col2.misses) < 2:        # too few missing
                        continue
                    #  now sliding down the cols
                    for d in range(h+1,9):
                        if col1.line[d] == ' ' and col2.line[d] == ' ':
                            print 'corner 0,1',corner0,corner1,d
                            pble = []
                            pble.append(r.possible[corner0])
                            pble.append(r.possible[corner1])
                            pble.append(col1.possible[d])
                            pble.append(col2.possible[d])
                            hit = self.analyse_quadruple(pble,True)
                            if not hit:
                                print 'hier gibts einen Nichtgeher'
##                            if hit:
##                                if hit[0] == 0:
##                                    s = r.get_stamp_index(corner0)
##                                    s = ((r.position / 3)*3 + s[0],s[1])
##                                elif hit[0] == 1:
##                                    s = r.get_stamp_index(corner1)
##                                    s = ((r.position / 3)*3 + s[0],s[1])
##                                elif hit[0] == 2:
##                                    s = col1.get_stamp_index(d)
##                                    s = (s[0]*3 + (r.position % 3),s[1])
##                                elif hit[0] == 3:
##                                    s = col2.get_stamp_index(d)
##                                    s = (s[0]*3 + (r.position % 3),s[1])
##                                print 'FOUND', hit, 'set:',hit[1],'to',s
##                                self.stamps[s[0]].set_hit(s[1],hit[1])
##                                return True
        print 'out quadruple()', '-'*40
        return False #irgendwas

    def analyse_quadruple(self,possible,toplevel=False):
        #print 'analyse',possible
        solution = False
        for e,i in enumerate(possible):
            if len(i) == 1:
                continue
            for n in i:
                hit = self.try_solution(n,e,possible)
                solution = hit and toplevel    # possible set of digits found
                if solution:
                    break
                #print '%d auf %d' % (n,e),'-'*40
##                if not hit:
##                    print 'FOUND',possible
            if solution:
                break
            if toplevel and not solution:
                print 'hier gibts einen Nichtgeher',e,i,possible
        #print '+'*70
        return solution

    def try_solution(self,guess,index,possible):
        if index >= len(possible):
            return False
        funny = ((1,3),(0,2),(1,3),(0,2),)
        rest = []
        for e,i in enumerate(possible):
            if e == index:
                rest.append([guess])
            else:
                j = i[:]
                if guess in j and e in funny[index]:
                    j.remove(guess)
                rest.append(j)
        #print 'enter',guess,index,rest
        for e,i in enumerate(rest):
            if len(i) > 1:
                self.analyse_quadruple(rest)
            elif len(i) == 0:
                #print 'leerstand',rest
                print 'leerstand',rest,'#',guess,index,possible
                return False
        #print guess,index,rest
        return True

    def old_analyse_quadruple(self,possible):
        """hat nicht funktioniert:
irrige Annahme: wenn 4 Ziffern und eine kommt nur einmal vor, dann ist die
                dort richtig.
Quatsch, weil ueber die Diagonale gleiche Ziffern vorkommen duerfen.
"""
        print 'analyse',possible
        n = {}
        for j in possible:
            for i in j:
                if n.has_key(i):
                    n[i] += 1
                else:
                    n[i] = 1
        if len(n) > 4:
            return False
        if len(n) < 4:
            print 'FEHLER: Hoppla! Quadruple < 4????'
            return False
        hit = False
        for i in n.keys():
            if n[i] == 1:
                hit = i         # this one we looked for
                break
        if hit:
            for e,i in enumerate(possible):
                if hit in i:
                    hit = (e,hit)
        return hit

    def bummers(self,):
        for i in self.rows:
            #if i.position <> 7: continue
            i.find_bummers()
        for i in self.cols:
            i.find_bummers()
        return False

    def rebuild_from_stamps(self,):
        liste = self.dumped_list
        for s in self.stamps:
            s.rebuild(liste)
        self.list_load(liste)

    def build_stamps(self,):
        """stamps are 3x3 groups of elements; numbering from left to right,
from top to bottom."""
        liste = self.dumped_list
        stamps = []
        idx = [0,1,2,9,10,11,18,19,20]
        for l in (3,3,3+9+9,3,3,3+9+9,3,3,0):
            stamps.append(Stamp(self.excerpt(liste, idx)))
            idx = [i+l for i in idx]
        return stamps

    def build_rows(self,):
        """rows are len(9) lines of elements; numbering from top to bottom."""
        liste = self.dumped_list
        lines = []
        for i in range(9):
            idx = range(9*i, 9+9*i)
            lines.append(Line(self.excerpt(liste, idx)))
            lines[-1].position = i
        return lines

    def build_cols(self,):
        """cols are len(9) columns of elements; numbering from left to right."""
        liste = self.dumped_list
        lines = []
        for i in range(9):
            idx = range(i, 81, 9)
            lines.append(Line(self.excerpt(liste, idx)))
            lines[-1].position = i
        return lines

    def check(self,):
        ok = True
        for i in self.stamps:
            ok = ok and i.check()
        for i in self.rows:
            ok = ok and i.check()
        for i in self.cols:
            ok = ok and i.check()
        return ok

    def query_done(self,):
        ok = True
        for s in (self.stamps,self.rows,self.cols):
            for i in s:
                ok = ok and i.done
                if not ok:
                    return False
##                else:
##                    if hasattr(i,'position'):
##                        pos = i.position    #   diese Unterscheidung muss weg
##                    else:
##                        pos = i.index
##                    print i.line_type,pos,'done'
        return ok        

    def print_log(self,):
        for s in (self.stamps,self.rows,self.cols):
            for i in s:
                i.print_log()

    def link_partners(self,):
        for e,i in enumerate(self.stamps):
            i.index = e
            i.options = self.options
            i.link(self.rows, self.cols)

class Stamp:

    row_ids = ((0,1,2),(0,1,2),(0,1,2),
               (3,4,5),(3,4,5),(3,4,5),
               (6,7,8),(6,7,8),(6,7,8),
               )
    col_ids = ((0,1,2),(3,4,5),(6,7,8),
               (0,1,2),(3,4,5),(6,7,8),
               (0,1,2),(3,4,5),(6,7,8),
               )
    align_row = ['row',[[0,1,2],[3,4,5],[6,7,8]]]
    align_col = ['col',[[0,3,6],[1,4,7],[2,5,8]]]

    def __init__(self, pattern):
        self.stamp = pattern
        self.done = False
        self.misses = self.imiss()
        self.log = StringIO()
        self.guesses = 0
        self.line_type = 'stamp'

    def __str__(self,):
        return str(self.stamp)

    def link(self, rows, cols):
        self.rows = []
        for i in self.row_ids[self.index]:
            self.rows.append(rows[i])
        self.cols = []
        for i in self.col_ids[self.index]:
            self.cols.append(cols[i])

        segment = self.index % 3 
        for i in self.rows:
            i.link(self, segment, 'row')
            i.options = self.options
            
        segment = self.index / 3 
        for i in self.cols:
            i.link(self, segment, 'col')
            i.options = self.options

    def guess(self,):
        changed = False
        self.guesses += 1
        if self.done:
            return changed
        possible = {}
        if self.options.debug:
            self.info()
        for e,i in enumerate(self.stamp):
            if i <> ' ':
                continue
            possible[e] = self.guess_element(e)
        print >> self.log,'stamp %d:: (%d)' % (self.index,self.guesses), possible
        if self.options.debug:
            print '(2)',self.has,self.misses
            print possible
        # Paare lokalisieren  (im Moment nur 2er)
        self.find_pairs(possible,2)
        self.find_pairs(possible,3)
        mbn = {}            # moves by number
        positioned = []
        for m in self.misses:
            mbn[m] = []
        for k in possible.keys():
            p = possible[k]
            if 1 == len(p):
                print >> self.log,'stamp %d:: (%d)' % (self.index,self.guesses),'set %d cause len-1' % p[0]
                self.set_hit(k,p[0])
                positioned.append(p[0])
                if self.options.debug:
                    print '(3)',self.has,self.misses
            else:
                for i in p:
                    mbn[i].append(k)
        if positioned:
            changed = True
            if self.options.debug:
                print '(4)',self.has,self.misses
                print possible,positioned
            for p in positioned:
                del mbn[p]
        if self.options.debug:
            print '(5)',mbn
        # Paare lokalisieren  (im Moment nur 2er)
        self.find_pairs(mbn, 2)
        self.find_pairs(mbn, 3)
        # Nummern setzen, die nur ein Feld einnehmen können
        for m in mbn.keys():
            if 1 == len(mbn[m]):
                print >> self.log,'stamp %d:: (%d)' % (self.index,self.guesses),'set %d cause only field' % m
                self.set_hit(mbn[m][0],m)
                del mbn[m]      # löschen, damit er bei der Kandidatensuche
                changed = True  #       nicht mehr stört
        self.set_candidates(mbn)
        if changed:
            #print 'CHANGED'
            self.misses = self.imiss()            
        if 1 == len(self.misses):
            index = self.stamp.index(' ')
            value = self.misses[0]
            print >> self.log,'stamp %d:: (%d)' % (self.index,self.guesses),'set %d cause last field' % value
            self.set_hit(index,value)
            print >> self.log,'stamp %d:: (%d)' % (self.index,self.guesses),'self-check'
            ok = self.check()
            if not ok:
                print self.log.getvalue()
            changed = True
        #self.info()
        return changed

    def set_hit(self, index, value):
        print >> self.log,'stamp %d:: (%d)' % (self.index,self.guesses),'set::',value,'nach',index
        if index not in range(9):
            return
        self.stamp[index] = str(value)
        if ' ' == self.stamp[index]:
            self.stamp[index] = str(value)
        elif self.stamp[index] <> str(value):
            print >> self.log,'Fehler!!! Feld belegt (%s).' % self.stamp[index], \
                                                    'set::',value,'nach',index
            print self.log.getvalue()
        self.rows[index / 3].set_hit(3 * (self.index % 3) + index % 3,value)
        self.cols[index % 3].set_hit(3 * (self.index / 3) + index / 3,value)
        self.misses = self.imiss()            

    def guess_element(self, index,):
        p = []
        ar = self.rows[index / 3]   # associated row
        ac = self.cols[index % 3]
        for j in self.misses:
            if j in ar.has:
                continue
            if ar.candidates.has_key(j) and ar.candidates[j] <> self.index:
                if self.options.debug:
                    print 'stamp %d:: (%d) @ %d' % (self.index,self.guesses,index), \
                          j,'ist Cand. in',ar.candidates[j]
                continue
            if j in ac.has:
                continue
            if ac.candidates.has_key(j) and ac.candidates[j] <> self.index:
                if self.options.debug:
                    print 'stamp %d:: (%d) @ %d' % (self.index,self.guesses,index), \
                          j,'ist Cand. in',ac.candidates[j]
                continue
            p.append(j)
        return p

    def set_candidates(self, pattern):
        """Looks for special candidate patterns in 'pattern' and sets them;
Candidate is a number, that can be on two or three fields only, that are aligned
in row or column.
'pattern' is a dict {number:[fields,...], ...}
"""
        for n in pattern.keys():
            lp = len(pattern[n])
            if 2 > lp or 3 < lp:
                continue            # only 2 or 3 fields can align
            line = self.is_aligned(pattern[n])
            if line:
                if 'col' == line[0]:
                    # pattern wird vielleicht gar nicht gebraucht
                    self.cols[line[1]].set_candidates(pattern[n],n,self.index)
                if 'row' == line[0]:
                    self.rows[line[1]].set_candidates(pattern[n],n,self.index)

    def find_pairs(self,mbn,count):
        if len(self.misses) <= count:
            return          # not enough candidates for pairs
        pairs = {}
        for m in mbn.keys():
            p = mbn[m]
            if len(p) == count:
                pt = tuple(p)
                if pairs.has_key(pt):
                    pairs[pt].append(m)
                else:
                    pairs[pt] = [m]
        for p in pairs.keys():
            if len(pairs[p]) == count:  # Paar gefunden: p ist tuple von 2 Feldern
               # erscheint mir jetzt verkehrt herum; müsste in mbn detektiert werden!!!!!!!!!!!!!!
                if self.options.debug:
                    print 'Paar gefunden',pairs[p],'auf',p
                for m in mbn.keys():
                    if m in pairs[p]:   # die Zahl gehört zum Paar
                        continue
                    for i in mbn[m][:]:
                        if i in p:      # Feld ist von Paar belegt
                            mbn[m].remove(i)
                            if self.options.debug:
                                print i,'removed',mbn

    def is_aligned(self,fields):
        rc = False
        if 2 == len(fields):
            for i in (self.align_row,self.align_col):
                for e,j in enumerate(i[1]):
                    if fields[0] in j and fields[1] in j:
                        rc = i[0],e
                        break
        elif 3 == len(fields):
            f = fields[:]
            f.sort()
            for i in (self.align_row,self.align_col):
                if f in i[1]:
                    rc = i[0],i[1].index(f)
                    break
        return rc
            
    def ihave(self,):
        return [int(a) for a in self.stamp if a <> ' ']

    def imiss(self,):
        self.has = self.ihave()
        if 9 == len(self.has):
            self.done = True
            return []
        miss = range(1,10)
        for i in self.has:
             if i in miss:
                 miss.remove(i)
        return miss

    def rebuild(self, liste):
        for i in range(3):
            start = self.rows[i].position * 9 + self.cols[0].position
            liste[start:start+3] = self.stamp[3*i:3*i+3]

    def check(self,):
        ok = True
        done = []
        for i in self.has:
            if i in done:
                ok = False
                print 'ALARM stamp',self.index,i,self.has,self.misses,done
                break
            done.append(i)
        print >> self.log,'stamp %d:: (%d)' % (self.index,self.guesses),self.has,done
        return ok

    def info(self,):
        print 'stamp', '@ %d  guess (%d)' % (self.index,self.guesses)
        print ' ', self.stamp
        print 'have', self.has
        print 'miss', self.misses

    def print_log(self,):
        self.info()
        print self.log.getvalue()
        self.log.close()
        self.log = StringIO()

class Line:

    def __init__(self, pattern):
        self.line = pattern
        self.done = False
        self.stamps = [0,0,0]
        self.misses = self.imiss()
        self.candidates = {}        # Liste für Kanditaten
        self.log = StringIO()
        self.guesses = 0
        self.get_index_by_type = {'col': self.get_stamp_index_col,
                                  'row': self.get_stamp_index_row,
                                  }
        self.get_conversion_by_type = {'col': lambda x: x / 3,
                                       'row': lambda x: x % 3,
                                       }

    def __str__(self,):
        return str(self.line)

    def link(self, stamp, segment, line_type):
        self.stamps[segment] = stamp
        self.line_type = line_type
        self.get_stamp_index = self.get_index_by_type[line_type]
        self.get_stamp_conversion = self.get_conversion_by_type[line_type]

    def get_stamp_index_col(self, index):
        """Return (segment,index) of associated stamps;
segment = nr of stamp (0..2)
index   = stamp index
"""
##        print 'col',self.position,'stips',index, \
##              '-> s%d :: %d*3 + %d = %d' % (index / 3,(index % 3),self.position % 3,
##                        (index % 3)*3 + self.position % 3)
        return (index / 3, (index % 3)*3 + self.position % 3)

    def get_stamp_index_row(self, index):
        """see get_stamp_index_col()"""
##        print 'row',self.position,'stips',index, \
##              '-> s%d :: %d*3 + %d = %d' % (index / 3,(self.position % 3),index % 3,
##                        (self.position % 3)*3 + index % 3)
        return (index / 3, (self.position % 3)*3 + index % 3)

    def ihave(self,):
        return [int(a) for a in self.line if a <> ' ']

    def imiss(self,):
        self.has = self.ihave()
        if 9 == len(self.has):
            self.done = True
            return []
        miss = range(1,10)
        for i in self.has:
             if i in miss:
                 miss.remove(i)
        return miss

    def guess(self,):
        changed = False
        self.guesses += 1
        if self.done:
            return changed
        possible = {}
        if self.options.debug:
            self.info()
        for e,i in enumerate(self.line):
            if i <> ' ':
                continue
            possible[e] = self.guess_element(e)
        print >> self.log,self.line_type,'%d:: (%d)' % \
                                      (self.position,self.guesses), possible
        if self.options.debug:
            print '(2)',self.has,self.misses
            print possible
        # Paare lokalisieren  (im Moment nur 2er)
        self.find_pairs(possible,2)
        self.find_pairs(possible,3)
        mbn = {}            # moves by number
        positioned = []
        for m in self.misses:
            mbn[m] = []
        for k in possible.keys():
            p = possible[k]
            if 1 == len(p):
                print >> self.log,self.line_type,'%d:: (%d)' % \
                      (self.position,self.guesses),'set %d cause len-1' % p[0]
                segment,idx = self.get_stamp_index(k)
                self.stamps[segment].set_hit(idx,p[0])
                positioned.append(p[0])
                if self.options.debug:
                    print '(3)',self.has,self.misses
            else:
                for i in p:
                    mbn[i].append(k)
        self.possible = possible
        if positioned:
            changed = True
            if self.options.debug:
                print '(4)',self.has,self.misses
                print '(4)',possible,positioned
            for p in positioned:
                #print p,mbn
                del mbn[p]
        if self.options.debug:
            print '(5)',mbn
        # Paare lokalisieren  (im Moment nur 2er)
        self.find_pairs(mbn,2)
        self.find_pairs(mbn,3)
        # Nummern setzen, die nur ein Feld einnehmen können
        for m in mbn.keys():
            if 1 == len(mbn[m]):
                print >> self.log,self.line_type,'%d:: (%d)' % \
                        (self.position,self.guesses),'set %d cause only field' % m
                segment,idx = self.get_stamp_index(mbn[m][0])
                self.stamps[segment].set_hit(idx,m)
                changed = True
        if changed:
            self.misses = self.imiss()            
        if 1 == len(self.misses):
            index = self.line.index(' ')
            value = self.misses[0]
            segment,idx = self.get_stamp_index(index)
            print >> self.log,self.line_type,'%d:: (%d)' % (self.position,self.guesses), \
                            ':: Loch',value,'in',index, '(seg %d, idx %d)' % (segment,idx)
            self.stamps[segment].set_hit(idx,value)
            changed = True
            print >> self.log,self.line_type,'%d:: (%d)' % (self.position,self.guesses),'self-check'
            ok = self.check()
            if not ok:
                print self.log.getvalue()
        return changed

    def guess_element(self, index,):
        p = []
        segment,idx = self.get_stamp_index(index)
        stamp = self.stamps[segment]            # associated stamp
        if 'col' == self.line_type:
            line = stamp.rows[index % 3]        # associated line (crossing)
        else:
            line = stamp.cols[index % 3]        # associated line (crossing)
        for j in self.misses:
            if j in stamp.has:
                continue
            if j in line.has:
                continue
            if self.candidates.has_key(j) and \
               self.candidates[j] <> self.stamps[index / 3].index:
                if self.options.debug:
                    print 'stamp %d:: (%d) @ %d' % (self.position,self.guesses,index), \
                          j,'ist Cand. in',self.candidates[j]
                continue
            if line.candidates.has_key(j) and \
               line.candidates[j] <> self.stamps[index / 3].index:
                if self.options.debug:
                    print 'stamp %d:: (%d) @ %d' % (self.position,self.guesses,index), \
                          j,'ist Cand. in',line.candidates[j]
                continue
            p.append(j)
        return p
            
    def find_pairs(self,mbn,count):
        if len(self.misses) <= count:
            return          # not enough candidates for pairs
        pairs = {}
        for m in mbn.keys():
            p = mbn[m]
            if len(p) == count:
                pt = tuple(p)
                if pairs.has_key(pt):
                    pairs[pt].append(m)
                else:
                    pairs[pt] = [m]
        for p in pairs.keys():
            if len(pairs[p]) == count:  # Paar gefunden: p ist tuple von 2 Feldern
                if self.options.debug:
                    print 'Paar gefunden',pairs[p],'auf',p
                for m in mbn.keys():
                    if m in pairs[p]:   # die Zahl gehört zum Paar
                        continue
                    for i in mbn[m][:]:
                        if i in p:      # Feld ist von Paar belegt
                            mbn[m].remove(i)
                            if self.options.debug:
                                print i,'removed',mbn

    def check(self,):
        ok = True
        done = []
        for i in self.has:
            if i in done:
                ok = False
                print 'ALARM',self.line_type,self.position,i,self.has,self.misses,done
                break
            done.append(i)
        print >> self.log,self.line_type,'%d:: (%d)' % (self.position,self.guesses),self.has,done
        return ok

    def set_hit(self, index, value):
        print >> self.log,self.line_type,'%d:: (%d)' % (self.position,self.guesses),'set::',value,'nach',index
        if ' ' == self.line[index]:
            self.line[index] = str(value)
        elif self.line[index] <> str(value):
            print >> self.log,'Fehler!!! Feld belegt (%s).' % self.line[index], \
                                        'set::',value,'nach',index
            print self.log.getvalue()
        if self.candidates.has_key(value):
            del self.candidates[value]
        self.misses = self.imiss()

    def set_candidates(self, pattern, value, stamp):
        # pattern brauch ich wahrscheinlich gar nicht
        if value in self.has:
            print self.line_type, '@ %d' % self.position,'candidate',value,'hab ich schon fest'
        else:
            #p = [self.get_stamp_conversion(i) for i in pattern]
            if self.candidates.has_key(value) and \
               stamp <> self.candidates[value]:
                print self.line_type, '@ %d' % self.position,'candidate',value, \
                      'hab ich schon als Cand. (%d <> %d)' % (stamp,self.candidates[value])
            else:
                self.candidates[value] = stamp
            if self.options.debug:
                print self.line_type, '@ %d' % self.position,'candidates',self.candidates

    def find_bummers(self,):
        if len(self.misses) < 2:
            return
        self.info()
        print 'possible',self.possible
        for i in self.possible.keys():
            for n in self.possible[i]:
                lines = self.try_solution(n,i,self.possible)
                print '%d auf %d' % (n,i),lines,'-'*40
                if len(lines) < 1:
                    print 'FOUND'
                    self.info()
        print '+'*70
        return

    def try_solution(self,guess,index,possible):
        if not possible.has_key(index):
            return False
        if len(possible) == 1:
            return [[guess]]
        lines = []
        used = [guess]
        rest = possible.copy()
        #print 'enter',guess,index,possible
        del rest[index]
        for i in rest.keys():
            new_rest = rest[i][:]
            for j in rest[i]:
                if j in used:
                    new_rest.remove(j)
                    #print i,': removed',j,new_rest
            rest[i] = new_rest
        i = rest.keys()[0]
        #print 'in second',i,used,rest
        if len(rest[i]) > 0:
            for j in rest[i]:
                ret = self.try_solution(j,i,rest)
                #print 'returned',ret
                if not ret:
                    continue
                for r in ret:
                    lines.append(used + r)
                #print 'recurse',i,j,lines
        else:
            return False
        #print 'ende',used,lines
        if len(used) == len(possible):
            lines.append(used)
        return lines

    def info(self,):
        print self.line_type, '@ %d  guess (%d)' % (self.position,self.guesses)
        print '  member of', [a.index for a in self.stamps]
        print ' ',self.line
        print '  have', self.has
        print '  miss', self.misses

    def print_log(self,):
        self.info()
        print self.log.getvalue()
        self.log.close()
        self.log = StringIO()

        
def usage(progname):
    usg = """usage: %s <...>
  %s""" % (progname,__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    parser.add_option("-d", "--debug",
                  action="store_true", dest="debug", default=False,
                  help="print debug information to stdout")
    parser.add_option("-q", "--quiet",
                  action="store_true", dest="quiet", default=False,
                  help="suppress printing to stdout")
    name,test = testfall()
    parser.add_option("-g", "--game",
                  dest="name", default=name,
                  help="""set game to the specified; ['%s'];""" % name)
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args
        print todo
        print "Testfälle:"
        for i in test_faelle.keys():
            print i
        sys.exit()
    name,test = testfall(options.name)
    game = Sudoku(test,name,options=options)
    root = Tk()
    display = sudokuChart(root,game)
    root.mainloop()
