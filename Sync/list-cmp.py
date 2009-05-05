#!/usr/bin/python
# -*- coding: utf-8 -*-
"""vergleicht Dateien aus einem sync-log-File stückweise mit dos2unix"""

import sys, os
from optparse import OptionParser

TEMPFILE = 'py__tmp.py'

class Todo:
    def __init__(self,name,s_on='',s_off=''):
        f = file(name)
        if s_on:
            l = f.readline()
            while not l.startswith(s_on):
                l = f.readline()
        tl = []
        while 1:
            l = f.readline()
            if s_off and l.startswith(s_off):
                break
            tl.append(l.rstrip('\n'))
        f.close()
        self.todo_liste = self.convert(tl)
        return
    def convert(self,liste):
        tl = []
        for l in liste:
            a = l.split()
            if len(a) != 3:
                print 'warning: erroneous blanks!!', l
            else:
                tl.append([os.path.join(a[0],a[2]),a[2]])
        return tl

def compare(lfile,rpath):
    source = lfile
    if not options.windows:
        r = os.system('dos2unix -n %s %s >/dev/null 2>&1' % (lfile,TEMPFILE))
        source = TEMPFILE
    #print 'dos2unix ---->', r
    print lfile
    p = os.popen('diff %s %s' % (source,rpath))
    r = p.read()
    p.close()
    if not options.windows:
        os.remove(TEMPFILE)
    if r:
        print r
        r = 1
    #print 'diff ---->', r
    return r
    
def usage(progname):
    usg = """usage: %s [options] sync-log target-directory
  %s""" % (progname,__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    parser.add_option("-w", "--windows",
                  action="store_true", dest="windows", default=False,
                  help="do not convert with dos2unix")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage(os.path.basename(sys.argv[0]))
    (options, args) = parser.parse_args()
    if len(args) < 2:
        print usg
        sys.exit(1)
    if options.verbose:
        print options,args
    #sys.exit(0)
    sync = args[-2]
    target = args[-1]
    todo = Todo(sync,s_on='different',s_off='only in')
    results = []
    for i in todo.todo_liste:
        results.append([i[0],compare(i[0],os.path.join(target,i[0]))])
    for i in results:
        if options.verbose or i[1]:
            print i[1], i[0]
