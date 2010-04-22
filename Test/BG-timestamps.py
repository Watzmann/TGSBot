#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Hier wird der bei BG-Spielen so beliebte timestamp umgerechnet."""

from time import *
import math

import sys
from optparse import OptionParser

def usage(progname):
    usg = """usage: %s <...>
  %s""" % (progname,__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    return parser,usg

def magnitude(mag):
    """returns a power of 10 according to the aproximat magnitude 'mag'"""
    a = int(round(mag))
    ret = '1'+'0'*a
    return float(ret)

def convert(arg):
    try:
        f = float(arg)
    except:
        print '%s should be a float' % arg
        return
    a = f/magnitude(math.log10(f/time()))
    return ctime(a)

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args
    if len(args) < 1:
        args = [time(),]

    for a in args:
        print convert(a)
