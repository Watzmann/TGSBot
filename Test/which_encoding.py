#!/usr/bin/python
# -*- coding: latin-1 -*-
u"""Prüft, welche Unicode-Codierung bei der angegebenen Datei vorliegt."""

import sys
from optparse import OptionParser

EC = ['   latin-1',
      '    cp1252',
      '     utf-8',
      'iso-8859-1',
      ]

def usage(progname):
    usg = """%prog <...>
  """ + __doc__
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    return parser,usg

def get_body(fname):
    f = file(fname)
    r = f.read()
    f.close()
    return r

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args
    if len(args) < 1:
        parser.print_usage()
        print "!! Bitte Dateinamen angeben"
        sys.exit(1)

    filename = args[0]
    string = get_body(filename)
    for i in EC:
        try:
            d = string.decode(i)
            print 'hat funktioniert mit', i
        except:
            print ' schief gegangen mit', i
