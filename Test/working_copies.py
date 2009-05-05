#!/usr/bin/python
# -*- coding: utf-8 -*-
u"""
  working_copies.py erzeugt eine Liste von Subversion Working Copies.

  Es können mehrere root-Verzeichnisse angegeben werden.
  Ist das erste Argument "-", so wird die Liste von Kandidaten von stdin
  gelesen. Die Liste sollte Verzeichnisse enthalten, die mit "/.svn" enden.

  Beispiele:
              working_copies.py /var/develop
              locate -b .svn|grep '\.svn$'|working_copies.py -"""

import sys
import os
from subprocess import Popen, PIPE, call
from optparse import OptionParser

BUFSIZE = 4096

##good = ['./ImportExport','./ListTool.BICsvn',
##                     './ListTool','./scripts',
##                     './Python/Source','./Python/UML']

class WorkingCopies:
    def __init__(self, root, source_stdin=False):
        if source_stdin:
            self.found = sys.stdin.read().splitlines()
        else:
            cmd = "find %s -name '.svn' -prune" % root
            p = Popen(cmd, shell=True, bufsize=BUFSIZE, stdout=PIPE,).stdout
            self.found = p.read().splitlines()
            p.close()
        self.condense()

    def condense(self,):
        wc = {}
        for f in self.found:
            s = os.path.dirname(f)
            parent,base = os.path.split(s)
            c,h,p,b = self.condense_2(wc,parent,base)
            while c and not h:
                c,h,p,b = self.condense_2(wc,p,b)
            if h:
                pass #print 'f old', b, p
            else:
                if base in wc:
                    wc[base].append(parent)
                else:
                    wc[base] = [parent]
                #print 'h neu', base, parent
        ret = self.condense_3(wc)
        while ret:
            ret = self.condense_3(wc)
        self.copies = wc
        return

    def condense_2(self, wc, parent, base):
##        print 'condense_2', parent, base
        p,b = os.path.split(parent)
        if b in wc and p in wc[b]:
##            print 'found',b,'for',base
            ret = True
        else:
            ret = False
        return p not in ['',os.sep], ret, p, b

    def condense_3(self, wc):
        redo = False
        for k,v in wc.items():
            for i in v[:]:
##                print '_3',k,i
                #parent,base = os.path.split(i)
                #c,h,p,b = self.condense_2(wc,parent,base)
                c,h,p,b = self.condense_2(wc,i,k)
                while c and not h:
                    c,h,p,b = self.condense_2(wc,p,b)
                if h:
##                    print '_3 removing',i,'from',v
                    v.remove(i)
                    redo = True
            if len(v) == 0:
                del wc[k]
        return redo

def print_sorted(wc):
    plist = []
    for i,v in wc.copies.items():
        for j in v:
            plist.append(os.path.join(j,i))
    plist.sort()
    for p in plist:
        print p

def usage():
    usg = """usage: %%prog [options] [-] [<root>,...]
  %s""" % (__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    return parser,usg

if __name__ == "__main__":
    parser,usg = usage()
    (options, args) = parser.parse_args()
    if options.verbose:
        print options,args

    if len(args) == 0:      # root-Verzeichnisse für die Suche
        roots = ['']
    else:
        roots = args

    if roots[0] == '-':
        wc = WorkingCopies('', True)
        print_sorted(wc)
    else:
        for r in roots:
            if r and os.path.exists(r) and os.path.isdir(r):
                root = r
            elif r == '':
                root = r

            if options.verbose:
                print 'root', root

            wc = WorkingCopies(root)
            print_sorted(wc)
