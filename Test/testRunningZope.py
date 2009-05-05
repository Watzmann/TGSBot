#!/usr/bin/python
# -*- coding: utf-8 -*-
"""ermittelt laufende Zope-Instanzen"""

import sys, os
from optparse import OptionParser

def readInstances():
    liste = []
    p = os.popen("ps aux|grep zope")
    liste_raw = [l.strip('\n') for l in p.readlines()]
    liste = []
    for lr in liste_raw:
        a = lr.split()
        if a[0].startswith('zope'):
            liste.append([a[0],a[-1]])
    return liste

def versuch(source):
    #print 'lese', source
    ports = {}
    for k in g.Text.keys():
        #print (k+' + ')*8
        #print g.Text[k]
        lines = g.Text[k].split('\n')
        for line in lines:
            if line.lstrip().startswith('#'):
                #print 'iss so',line.lstrip()
                continue
            if 'address' in line:
                a = line.split()
                #print '##########',k,a[1]
                ports[k] = a[1]
    return ports
    
def usage(progname):
    usg = """usage: %s <...>
  %s""" % (progname,__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args
    running_raw = readInstances()
    for r in running_raw:
        print r
