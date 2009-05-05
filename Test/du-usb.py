#!/usr/bin/python
# -*- coding: utf-8 -*-
"""liefert den belegten Speicherplatz des angegebenen Mediums (du -s ...*)"""

import sys, os
from optparse import OptionParser

def usage(progname):
    usg = """usage: %s [<media>]
  %s""" % (progname,__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    parser.add_option("-s", "--size_left", dest="size_left", default=None,
                  help="print size left on device. Argument is total size [256]")
##    def_format = 'MB'
##    parser.add_option("-f", "--format",
##                  dest="format", default=def_format,
##                  help="""set output format to one of 'B,kB,MB,GB';
##                default is %s.""" % def_format)
    return parser,usg

def doit(target):
    #return 120.234
    target = target.rstrip('/')
    if options.verbose:
        print 'Verbrauchter Platz auf',target
    p = os.popen('du -s %s/*' % target)
    r = p.readlines()
    summe = 0
    for l in r:
        a = l.split()
        summe += int(a[0])
        if options.verbose:
            print '%6s  %s' % (a[0],a[1])
    return summe/1024.

def media(lines):
    lm = []
    for ls in lines:
        a = ls.rstrip('\n').split()
        lm.append(a[2])
    return lm

def print_size(size):
    print '%.2f MB' % (size,),
    if options.size_left:
        print '(%.2f MB left)' % (float(options.size_left)-size,)
    else:
        print

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args
    if len(args) < 1:
        p = os.popen('mount|grep media')
        for m in media(p.readlines()):
            print m+':',
            sys.stdout.flush()
            print_size(doit(m))
    else:
        device = args[0]
        print device+':',
        sys.stdout.flush()
        print_size(doit(device))
    
