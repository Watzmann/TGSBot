#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""tar-listen.py gibt tar-Inhalte in gewünschter Tiefe aus"""

TODO = """1. tar-listen funktioniert nicht vom stdin - warum?
2. Warum tar? Am besten einfach nur tar nach stdin und pipen.
"""

import sys
import os
from listen import Liste
from el_listen import Line
from optparse import OptionParser

DEF_DEPTH = 2

class My_Liste(Liste):

    def __init__(self, liste, **kw):
        Liste.__init__(self, liste, **kw)

    def my_filter(self, **kw):
        ls = []
        if kw.has_key('truncate') and kw['truncate']:
            for l in self._raw_liste:
                ls.append(os.path.dirname(l))
        else:
            for l in self._raw_liste:
                if l[-1] == '/':
                    ls.append(l)
        return ls

    def tar_reduce(self, depth=DEF_DEPTH):
        l = []
        for i in self.liste:
            a = i.split('/')
            if (depth == 0) or (len(a) < depth+2):
                l.append(i)
        return l

def usage(progname):
    usg = """usage: %s <...>
  %s""" % (progname,__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    parser.add_option("-t", "--truncate",
                  action="store_true", dest="truncate", default=False,
                  help="truncate files (basename) from line")
    def_depth = DEF_DEPTH
    parser.add_option("-d", "--depth",
                  dest="depth", default=def_depth, type='int',
                  help="""set listing depth; default is %d.""" % def_depth)
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args
    if len(args) < 1:
        args.append('-')

    #print args[0]
    kw = {'truncate':options.truncate}
    #print 'kw',kw
    l = My_Liste(args[0], **kw)
    l2 = Liste(l.tar_reduce(options.depth))
    for i in l2.interpret(Line):
        #print i.path
        print i
