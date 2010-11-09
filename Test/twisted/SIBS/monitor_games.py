#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tool zum Untersuchen und Warten der Users-DB."""

import sys
from optparse import OptionParser
from persistency import Persistent, Db
from time import *

def usage(progname):
    usg = """usage: %prog [<user>]
  %prog """ + __doc__
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print full entries to stdout")
    return parser,usg

if __name__ == '__main__':
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if len(args) > 0:
        gnr = args[0]
    else:
        gnr = ''

    db = Db('db/games')
    keys = db.db.keys()
    keys.sort()
    if gnr:
        keys = [keys[int(gnr)],]
    else:
        print 'saved games'
        for e,k in enumerate(keys):
            print e, k, asctime(localtime(float(k)/1000000.))

    for e,k in enumerate(keys):
        print e,k
        v = db.db[k]
        print '   ', v.position, v.cube, v.value, v.direction, v.move
    db.close()
