#!/usr/bin/python
# -*- coding: utf-8 -*-
"""gibt den path in der 'parallelen' Zope-Instanz zurück"""

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

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args
    if len(args) < 1:
        print usg
        print "!! Namen der parallelen Zope-Instanz angeben"
        sys.exit(1)

    hier = os.getcwd()
    root = '/var/opt/zope/'
    tail = hier[len(root):]
    a = tail.split(os.sep)
    if options.verbose:
        print a[0],'->',args[0]
    a[0] = args[0]
    newTail = os.sep.join(a)
    dort = os.path.join(root,newTail)
    print dort
