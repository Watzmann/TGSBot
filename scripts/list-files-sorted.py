#!/usr/bin/python
# -*- coding: utf-8 -*-
"""sorts list of files by optional criteria (date, ...)"""

_CopyRight = '(c) 2006  AHa.Doc. (Dr. Andreas Hausmann)'
_Version = '0.9'
_TODO = u"""Todos:
1) Grundsätzlich sollte ein ListenProzessor (gebaut und) benutzt werden.
   (also: nimm eine Liste (aus welcher Quelle auch immer) und mach was
    damit; hier handelt es sich oft um Listen von Files:
    - Existieren die Files aus dieser Liste auf dem Rechner?
    - Wurden diese Files verändert?
    - ...
1a)So müssen auch grundsätzlich folgende Listen verarbeitet werden:
    - files, die (zeilenweise) Listen enthalten.
    - mehrere Argumente auf der Commandozeile bilden eine Liste
    - stdin füttert eine Liste
2) andere Keys (als nur Datum) sollten eingebaut werden. Dann muss das
   Sort-Kriterium ausgewertet werden.
"""

import sys, os, time
from stat import *

from optparse import OptionParser

class ListOfFiles:
    def __init__(self, fname):
        self.fileList = []
        self.nr = 0
        if fname and os.path.exists(fname):
            f = file(fname)
            self.fileList = [a.strip('\n') for a in f.readlines()]
            f.close()
        self.entries = dict(zip(self.fileList,range(len(self.fileList))))
        return
    def sort(self):
        self.fileList.sort(key=self.elDate, reverse=options.reverse)
        return
    def diff(self):
        self.fileList.sort(key=self.elDate, reverse=options.reverse)
        return
    def elDate(self, element):
        if os.path.exists(element):
            st = os.stat(element)
            key = st[ST_MTIME]
            el_time = time.strftime('%d-%m-%y %H:%M',time.localtime(key))
            self.entries[element] = el_time
        else:
            key = self.nr
            self.nr += 1
            el_time = key
        if options.noisy:
            print '#',el_time,element
        return key
    def Key(self, element):
        return self.entries[element]
    def Liste(self):
        return self.fileList

def usage(progname):
    usg = u"""usage: %s <file>
  %s

  <file>    file containing list of files
            e.g. ``find -name '*.odp' > ah´´""" \
  % (progname,__doc__)
    parser = OptionParser(usg)
    parser.add_option("-V", "--version",
                  action="store_true", dest="version", default=False,
                  help=u"print version info, todos and exit")
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help=u"print status messages to stdout")
    parser.add_option("-n", "--noisy",
                  action="store_true", dest="noisy", default=False,
                  help=u"print details to stdout")
    parser.add_option("-r", "--reverse",
                  action="store_true", dest="reverse", default=False,
                  help=u"print list in reverse order")
    parser.add_option("-d", "--date",
                  action="store_true", dest="sort", default=False,
                  help=u"sort list of files by date")
    return parser,usg

if __name__ == "__main__":
    my_name = os.path.basename(sys.argv[0])
    parser,usg = usage(my_name)
    (options, args) = parser.parse_args()
    if options.version:
        print my_name,'version',_Version
        print _CopyRight
        print
        print _TODO
        sys.exit(0)
    if options.noisy:
        print 'OPTIONS'
        print options
        print 'ARGS'
        print args
    if len(args) < 1:
        print "!! not enough arguments; give list of files !!"
        print usg
        sys.exit(1)
    liste = ListOfFiles(args[0])
    if options.sort:
        liste.sort()
    for l in liste.Liste():
        if options.verbose:
            print liste.Key(l),
        print l
