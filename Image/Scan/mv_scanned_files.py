#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""Es werden _alle_ Dateien im angegebenen Verzeichnis um einen Offset
verschoben (umbenannt). Default-Verzeichnis ist '.'.
Das Skript ist gedacht für gescannte Dateien, bei denen ein Fehler in der
Nummerierung korrigiert werden soll."""

import sys
import os
import glob
from optparse import OptionParser

OFFSET = 260-187

def new_name(f):
    # change the 'name'-part of the filename according to a rule
    f = '%04d' % (int(f) + OFFSET)
    return f

def doit():
    processed_files = []
    for f in glob.iglob('*'):
        # moving to a working name to avoid filename clashes
        wf = '__%s_' % f
        os.rename(f, wf)
        # build the new name
        old = os.path.splitext(f)
        newf = new_name(old[0])
        newf = newf + old[1]
        # record all the names for later use
        processed_files.append((f, wf, newf))

    for f in processed_files:
        a,b,c = f
        # rename from working name to destination name
        os.rename(b,c)
        if options.verbose:
            print a,'->',c

def usage(progname):
    usg = """usage: %s [directory]
  %s""" % (progname,__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    parser.add_option("-O", "--offset",
                  action="store", dest="offset", default=OFFSET,
                  help="use given offset [%d]" % OFFSET)
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if len(args) < 1:
        wd = '.'
    else:
        wd = args[0]
        os.chdir(wd)
    if options.verbose:
        print options,args
        print 'working directory', wd
        print os.getcwd()
    
    doit()
    print 'done'
