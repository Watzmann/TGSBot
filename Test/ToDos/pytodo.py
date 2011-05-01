#!/usr/bin/python
# -*- coding: utf-8 -*-
"""User Interface für die ToDos auf Dropbox/ToDo"""

import sys
import os
from optparse import OptionParser
import globber

def usage(progname):
    usg = """usage: %s <...>
  %s""" % (progname,__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    tgt
    parser.add_option("-t", "--target",
                  action="store", dest="target", default=tgt,
                  help="print status messages to stdout")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args

    target 
