#!/usr/bin/python
# -*- coding: utf-8 -*-
"""vergleiche 2 Listen, die durch 'du -s' erstellt wurden"""

import sys,os
from optparse import OptionParser

class DuList:
    def __init__(self,fname):
        self.name = fname
        f = file(fname)
        liste = [a.strip('\n') for a in f.readlines()]
        while 1:
            try:
                liste.remove('')
            except:
                break
        self.orgListe = liste
        self.liste = self.procListe(self.orgListe)
        f.close()
        return
    
    def procListe(self,liste):
        pliste = {}
        nameList = [a.split()[-1] for a in liste]
        root = self.findRoot(nameList)
        r = len(root)+1
        for l in liste:
            a = l.split()
            pliste[a[1][r:]] = a[0]
        return pliste
    
    def findRoot(self,liste):
        if not liste:
            return ''
        root = liste[0]
        #print 'first',root
        found = False
        n=0
        while n<10 and not found and root:
            for e,i in enumerate(liste[1:]):
                if not i.startswith(root):
                    root = os.path.dirname(root)
                    #print 'broke',root
                    break
            found = len(liste) == e+2
            #print e+2,len(liste),found
            n+=1
        #print 'found',root
        return root

    def printListe(self):
        for k in self.liste.keys():
            print k,self.liste[k]
        return
    
    def lcmp(self,liste):
        l_here = (self.name,self.liste.copy())
        l_there = (liste.name,liste.liste.copy())
        self.cmp_l = cmp_l(l_here,l_there)
        return self.cmp_l.convResult()
    
class cmp_l:
# die compare-Routine setzt auf den Vergleich von 2 dicts auf
# sollte allgemein verwendbar sein
# (vielleicht besser als Klasse mit optionalen compare-Funktionen
# und Auswerte-Methoden)
    # folgende Dict-Keys werden für das Result-Dict verwendet
    both = 'both'
    only = 'only'
    same = 'same'
    diff = 'diff'
    path = 'path'
    value = 'value'
    here = 'here'
    there = 'there'

    def __init__(self,nl1,nl2):
    # n1,l1 = nl1 (name,dict)
    # n2,l2 dito
        self.both_d = {self.same:[],self.diff:[]}
        n1,l1 = nl1
        n2,l2 = nl2
        self.where = {self.here:n1,self.there:n2}
        same = []
        diff = []
        for k1 in l1.keys():
            if l2.has_key(k1):
                if l1[k1] == l2[k1]:
                    same.append({self.path:k1,self.value:l1[k1]})
                else:
                    diff.append({self.path:k1,self.value:(l1[k1],l2[k1])})
                del l1[k1]
                del l2[k1]
        both = {self.same:same,self.diff:diff}
        self.comparison = {self.both:both,self.only:{n1:l1,n2:l2}}
        return

    def ishere(self,names):
        if names[0] == self.where[self.here]:
            return (0,1)
        else:
            return (1,0)
    
    def convResult(self):
        """gibt Ergebnis in 4 Listen: (same,diff,only_here,only_there)"""
        c = self.comparison
        same = [v[self.path] for v in c[self.both][self.same]]
        diff = ['%s  (%s :: %s)' % ((v[self.path],)+v[self.value])
                                for v in c[self.both][self.diff]]
        only = c[self.only]
        names = only.keys()
        here,there = self.ishere(names)
        only_here = only[names[here]].keys()
        only_there = only[names[there]].keys()
        return (same,diff,only_here,only_there)

def usage(progname):
    usg = """usage: %s liste1 liste2
  %s""" % (progname,__doc__)
    parser = OptionParser(usg)
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
##    def_format = 'MB'
##    parser.add_option("-f", "--format",
##                  dest="format", default=def_format,
##                  help="""set output format to one of 'B,kB,MB,GB';
##                default is %s.""" % def_format)
    return parser,usg

def printMe(liste,bez):
    if liste:
        liste.sort()
        print bez+':'
        for d in liste:
            print ' ',d

if __name__ == "__main__":
    parser,usg = usage(sys.argv[0])
    (options, args) = parser.parse_args()
    if options.verbose:
        print options
        print args
    if len(args) < 2:
        print usg
        print "!! Zu wenige Argumente angegeben"
        sys.exit(1)
    liste1 = DuList(args[0])
    liste2 = DuList(args[1])
    if options.verbose:
        print liste1.name,'<->',liste2.name
##        print '#####',liste1.name
##        liste1.printListe()
##        print '#####',liste2.name
##        liste2.printListe()
    same,diff,only1,only2 = liste1.lcmp(liste2)
    if options.verbose:
        printMe(same,'same in both')
    printMe(diff,'differences')
    printMe(only1,'only in %s' % liste1.name)
    printMe(only2,'only in %s' % liste2.name)
        
    #sys.exit(0)
##    fname = args[0]
##    inhalt = Lines(fname)
##    fmt = options.format
##    print '%s: %d %s' % (inhalt.name,inhalt.sumsize(fmt=fmt),fmt)
