#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests zur Beschreibung von Modul OptParse (Python-Doku)"""

import sys, os
from optparse import OptionParser
#import ah_rename

def usage(progname):
    usg = """usage: %prog [<command>]
""" + __doc__
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    parser.add_option("--file-name",dest="fn" )
    return parser,usg


args = sys.argv #['--file-name','test.out']

parser,usg = usage('')
(options, args) = parser.parse_args(args)
print dir(options)
#print dir(parser)
print parser.prog
print OptionParser.standard_option_list
#print dir(ah_rename)
for i in sys.path:
    print i
