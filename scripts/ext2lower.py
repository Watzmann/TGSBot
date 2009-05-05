#!/usr/bin/python
# -*- coding: utf-8 -*-
"""moves the file-extension to lower case (.TIF -> .tif, ...)"""

import sys, os
from optparse import OptionParser

def usage(progname):
    usg = """usage: %s <...>
  %s""" % (progname,__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
##    def_format = 'MB'
##    parser.add_option("-f", "--format",
##                  dest="format", default=def_format,
##                  help="""set output format to one of 'B,kB,MB,GB';
##                default is %s.""" % def_format)
    return parser,usg

def doit(fname):
    old = fname
    new = ''
    print old,
    root,eold = os.path.splitext(old)
    if eold:
        enew = eold.lower()
        if eold != enew:
            new = root+enew
    if new:
        print '->', new
        os.rename(old, new)
    else:
        print
    
if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args
    if len(args) < 1:
        print usg
        print "!! give filename"
        sys.exit(1)

    doit(args[0])
