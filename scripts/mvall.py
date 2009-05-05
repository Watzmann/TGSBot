#!/usr/bin/python
# -*- coding: utf-8 -*-
"""benennt die Dateien im ganzen Directory um"""

import sys,os

from optparse import OptionParser

def usage(progname):
    usg = """usage: %s <alte Endung> <neue Endung>
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

def doit_mv(old,new):
    for i in os.listdir('.'):
        if options.verbose:
            print i,
        if i.endswith(old):
            idx = i.rfind(old)
            n = i[:idx] + new
            os.rename(i,n)
            replaced = '-> ' + n
        else:
            replaced = '---'
        if options.verbose:
            print replaced
    return

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if len(args) < 2:
        print usg
        print "!! Zu wenige Argumente angegeben"
        sys.exit(1)
    if options.verbose:
        print options,args
    doit_mv(args[0],args[1])
    #sys.exit(0)
##    fname = args[0]
##    inhalt = Lines(fname)
##    fmt = options.format
##    print '%s: %d %s' % (inhalt.name,inhalt.sumsize(fmt=fmt),fmt)
