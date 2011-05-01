#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""analysiert BG-Matches mit Aufruf von 'gnubg -tqp'"""

import os

print __name__
if __name__ == '__main__':
    root = '/home/hausmann/.gnubg'
    my_match = 'gnuBG-Andreas_7p_2010-02-21_1715.sgf'
    match = os.path.join(root,my_match)

    print match
    gnubg.command('load match %s' % match)
    gnubg.navigate()
    a = raw_input('kannst was eingeben ')
    while not a.startswith('q'):
        n = {'n':1,'p':-1}.get(a,0)
        m = {'y':1,'e':-1}.get(a,0)
        gnubg.navigate(next=n,game=m)
        gnubg.command('show board')
        a = raw_input('kannst was eingeben ')
