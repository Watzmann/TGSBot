#!/usr/bin/python
# -*- coding: utf-8 -*-
"""was macht das script"""

import sys
import os
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
        fname = 'el_listen.py'
    else:
        fname = args[0]

    keys = ['HEAD',
            'BASE',
            'COMMITTED',
            'PREV',
            ]
    for i in keys:
        print i, fname, '-'*50
        p = os.popen('svn info %s -r %s|grep Rev' % (fname,i))
        print p.read()
        p.close()
