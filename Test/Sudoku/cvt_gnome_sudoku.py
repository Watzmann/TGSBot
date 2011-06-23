#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Konvertiert Spiele aus gnome-sudoku in mein Format"""

# siehe auch /usr/lib/pymodules/python2.6/gnome_sudoku
# Beispiel:
#   014060300620004009080050600060200003070010050500009060006020030100500092007090410

import sys
import os

def convert(game):
    print "'gnome-': ("
    mg = game.replace('0','.')
    for i in range(0,81,9):
        sl = mg[i:i+9]
        print "    '%s'," % sl
    print "    ),"

if __name__ == '__main__':
    game = sys.argv[1]
    game = os.path.basename(game)
    convert(game)
