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
    def __init__(self, implemented_commands):
        help_file = open(os.path.join('ressources','help'))
        self.texte = dict(self.parse(help_file))
        self.issues = self.texte.keys()
        self.issues.sort
        self.tag(implemented_commands)  # TODO: implemented_commands can go
                                        #       when tag() is deleted

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

    def tag(self, implemented):
        """tag() tags commands in the 'help'-help with an asterisk,
    in order to give people information, which commands are implemented
    as yet.
    This method is supposed to be utilized so long as the full blown set
    of commands is not available.
    """
        doit = False
        lines = self.help_('help')
        for e,l in enumerate(lines):
            if l.startswith('  about'):
                doit = True
            elif len(l) < 5:
                break
            if doit:
                lines[e] = ' ' + l
                line = lines[e]
                a = l.split()
                for b in a:
                    if b in implemented:
                        c = line.find(b)
                        lines[e] = line[:c-1] + '+' + line[c:]
                        line = lines[e]

        lines += ["  + for the time being commands are prefixed with a " \
                  "'+' to indicate which\n",
                  "    commands are already available.\n"]

if __name__ == '__main__':
    h = Help(['about', 'accept', 'address', 'adios', 'board', 'bye'])
##    key = 'accept'
##    print key, h.texte[key]
    for c in sys.argv[1:]:
        for h in h.help_(c):
            print h,
            
