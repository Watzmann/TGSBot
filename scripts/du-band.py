#!/usr/bin/python
# -*- coding: utf-8 -*-
"""liest Inhalt von Streamer-Bändern und errechnet Speicherverbrauch"""

import sys
from optparse import OptionParser

class Lines:
    fmt_call = {
        '': 1.,
        'B': 1.,
        'kB': 1024.,
        'MB': 1024*1024.,
        'GB': 1024*1024*1024.,
        }
    def __init__(self, filename):
        self.name = filename
        f = file(filename)
        self.lines = [a.strip('\n') for a in f.readlines()]
        self.sizes()
        return
    def sizes(self):
        s = []
        for i in self.lines:
            #print i
            try:
                s.append(int(i.split()[2]))
            except:
                if options.verbose:
                    print 'discard',i
        self.fsizes = s
        return
    def lensize(self):
        return len(self.fsizes)
    def sumsize(self,fmt=''):
        s = float(sum(self.fsizes))
        return int(s/self.fmt_call[fmt])

def usage(progname):
    usg = """usage: %s <inhalts-file>
  %s""" % (progname,__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    def_format = 'MB'
    parser.add_option("-f", "--format",
                  dest="format", default=def_format,
                  help="""set output format to one of 'B,kB,MB,GB';
                default is %s.""" % def_format)
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    if len(sys.argv) < 2:
        print usg
        sys.exit(1)
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args
    #sys.exit(0)
    fname = args[0]
    inhalt = Lines(fname)
    fmt = options.format
    print '%s: %d %s' % (inhalt.name,inhalt.sumsize(fmt=fmt),fmt)
