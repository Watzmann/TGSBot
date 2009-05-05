#!/usr/bin/python
# -*- coding: latin-1 -*-
u"""Suche-Ersetze-Operationen in mehreren Dateien gleichzeitig ausführen."""

import sys
import os
from glob import glob
from optparse import OptionParser

def usage(progname):
    usg = """%prog <datei-liste> <suche> <ersetze>
  """ + __doc__.encode('utf-8') + """
  <datei-liste> ist eine Liste von Dateien.

Beispiele:
  %prog *.die 7DE02680-... CBA2AC1F-...
  %prog HUB.die INNEN.die KUERZEL.die 7DE02680-... CBA2AC1F-..."""
    parser = OptionParser(usg, conflict_handler='resolve')
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="gib Status-Meldungen auf der Console aus")
    parser.add_option("-o", "--overwrite",
                  action="store_true", dest="overwrite", default=False,
                  help="ersetze die Original-Tabellen (sonst erhalten sie die Endung '.new')")
    return parser

class Tabelle:

    def __init__(self,fname):
        self.filename = fname
        self.outfilename = self.out_filename(self.filename)
        f = file(fname)
        self.zeilen = f.readlines()
        self.output = self.zeilen[:]
        f.close()
        return

    def out_filename(self, filename):
        f = os.path.splitext(filename)
        fn = f[0] + '.new'
        return fn

    def write(self,overwrite=False):
        if overwrite:
            ofn = self.filename
        else:
            ofn = self.outfilename
        f = file(ofn,'w')
        f.writelines(self.output)
        return

    def substitute(self, find, replace):
        self.output = []
        for l in self.zeilen:
            self.output.append(l.replace(find,replace))
        return

if __name__ == "__main__":
    parser = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args
    if len(args) < 3:
        parser.print_usage()
        print "!! Zu wenige Argumente angegeben !!", \
                u"(Option -h für Hilfe)".encode('utf-8')
        sys.exit(1)

    find = args[-2]
    repl = args[-1]
    list_of_files = args[0:-2]

    if 1 == len(list_of_files):
        list_of_files = glob(list_of_files[0])

    if options.verbose:
        print list_of_files

    for filename in list_of_files:
        f = Tabelle(filename)
        f.substitute(find,repl)
        f.write(overwrite=options.overwrite)
