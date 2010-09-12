#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Utilities für SIBS.
"""

REV = '$Revision$'

import os
from version import Version
from sibs_utils import render_file

v = Version()
v.register(__name__, REV)

#def render_file(filename):

class Help:
    def __init__(self,):
        help_txt = render_file('help.txt')
        self.texte = dict(self.parse(help_txt))

    def parse(self, txt):
        name = ''
        liste = []
        flag = 0
        for i in txt:
            if flag:
                name = i.split()[0]
                lines = [first_line, i]
                flag = 0
            elif i.startswith('NAME'):
                if name:
                    liste.append((name,lines))
                flag = 1
                first_line = i
            else:
                lines.append(i)

if __name__ == '__main__':
    h = Help()
    key = 'accept'
    print key, h.texte[key]
