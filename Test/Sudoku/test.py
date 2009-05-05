#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test von Sudoku"""

from sudoku import *

class Options:
    def __init__(self,):
        self.verbose = False
        self.debug = False
        self.quiet = True
    def __str__(self,):
        return str(self.__dict__)

options = Options()
##print options

def build_line(pattern):
    lines = []
    for i in pattern:
        lines.append(i)
        lines.append([i[0],i[1]])
        lines.append([i[0],i[2]])
        lines.append([i[1],i[2]])
    return lines

def test_is_aligned():
    """Testet einige Konstellationen von 2er- und 3er-Tupeln auf Alignment.

DIES GEHOERT IN EINEN UNITTEST TESTCASE!

Getestet wird die Funktion Sudoku.is_aligned().
Es werden einige gute Konstellationen aufgebaut und nicht geprueft.
Es werden einige gute und schlechte Konstellationen aufgebaut und gegen die
eben erzeugten guten geprueft. Das Testergebnis wird in jedem Falle ausgegeben.
"""
    n,t = testfall()

    S=Sudoku(t,n,options=options)
    s=S.stamps[0]

    good_rows = build_line(([0,1,2],[3,4,5],[6,7,8]))
    good_cols = build_line(([0,3,6],[1,4,7],[2,5,8]))
    bad_rows = build_line(([1,3,6],[1,2,7],[2,5,7]))

    check = {}
    for f in (good_rows,good_cols,):
        for i in f:
            ss = s.is_aligned(i)
            check[tuple(i)] = ss

    print '-'*40
    for f in (bad_rows,):
        for i in f:
            ss = s.is_aligned(i)
            if ss:
                ok = ss == check[tuple(i)]
            else:
                ok = not check.has_key(tuple(i))
            print i,ss,'\t\t',ok

if __name__ == '__main__':
    #test_is_aligned()

    additional = filter(lambda x: len(x[0]) == 11, zeit_archiv.items())
    test_faelle.update(additional)

    tfk = test_faelle.keys()
    tfk.sort()
    #tfk = []
    #tfk = ['test427']
    #tfk = ['test519']
    #tfk = ['rhpf070218']
    for tf in tfk:
        name,test = testfall(tf)
        game = Sudoku(test,name,options=options)
        cycles = 0
        while True:
            cycles += 1
            cont,msg = game.next()
            if not cont:
                break
        print '%15s: after %d cycles: %s' % (name,cycles,msg)
                    

##  r73 | hausmann | 2007-02-13 17:30:12 +0100 (Di, 13 Feb 2007)
##        test423: after 9 cycles: done
##        test424: after 5 cycles: -stuck-
##    zeit070210s: after 6 cycles: done
##    zeit070211s: after 6 cycles: done
##        test023: after 3 cycles: done
##    zeit070210m: after 4 cycles: done
##    zeit070210l: after 5 cycles: done
##        test165: after 6 cycles: done
