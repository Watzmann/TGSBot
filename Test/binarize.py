#!/usr/bin/python
# -*- coding: utf-8 -*-
"""binarize.py binarizes gray scale scans to black and white.
  It employs the Netpbm package:
    - pamditherbw
    - pamtopnm
    - pnmtotiff
  Multiple args are taken to be multiple input files.
"""

import sys
import os
from subprocess import Popen, PIPE, call
from optparse import OptionParser

def binarize(source, value='0.5'):
    filein = source
    s = os.path.splitext(source)
    fileout = s[0] + '.bw.tif'
    print 'binarize', filein, fileout
    cmd = "pamditherbw -threshold -value %s %s | pamtopnm | \
pnmtotiff -g3 > %s" % (value, filein, fileout)
    #print cmd
    retcode = call(cmd, shell=True)
    if retcode > 0:
        print 'ERROR:', retcode, 'with', source
        sys.exit(retcode)
    return

def usage():
    usg = """usage: %%prog {*.pnm}
  %s""" % (__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    parser.add_option("-t", "--threshold", dest="threshold", default='0.5',
                  help="set threshold (0.1 ... 0.9) [0.5]")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage()
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args
    if len(args) < 1:
        print usg
        print "!! arguments missing"
        sys.exit(1)

    for i in args:
        binarize(i, value=options.threshold)
