#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Utilities für SIBS.
"""

REV = '$Revision$'

import sys
import os
from version import Version

v = Version()
v.register(__name__, REV)

#def render_file(filename):

class Help:
    def __init__(self,):
        help_file = open(os.path.join('ressources','help'))
        self.texte = dict(self.parse(help_file))
        self.issues = self.texte.keys()
        self.issues.sort

    def parse(self, hfile):
        name = ''
        liste = []
        flag = 0
        lines = []
        for line in hfile:
##            print 'parsing: name  %s    flag %d' % (name, flag)
##            print line
            if flag:
                name = line.split()[0]
                lines = [first_line, line]
                flag = 0
            elif line.startswith('NAME'):
                if name:
                    liste.append((name,lines))
##                    print name, '='*120
##                    print lines
                flag = 1
                first_line = line
            else:
                lines.append(line)
##        print 'about to return'
##        print liste[:2]
        return liste

    def help_(self, cmd):
        ret = self.texte.get(cmd, "no help on topic '%s'" % cmd)
        return ret

if __name__ == '__main__':
    h = Help()
##    key = 'accept'
##    print key, h.texte[key]
    for c in sys.argv[1:]:
        for h in h.help_(c):
            print h,
            
