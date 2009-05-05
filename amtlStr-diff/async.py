#!/usr/bin/python
# -*- coding: utf-8 -*-
"""vergleicht amtliches Straßenverzeichnis STE

(c) 05/2006 Andreas Hausmann
"""

import sys,os
from optparse import OptionParser

class Diff:
    """Difference assoziation between List-Classes."""

    def __init__(self,left,right):
        self.leftList = left
        self.leftPath = left.path
        self.rightList = right
        self.rightPath = right.path
        self.toggle = True
        return
        
    def printDiff(self, level='diff'):
        """Print out the differences found.

        Keyword 'level' = all|diff|left|right.
        """
        def printSimple(node, hold=False):
            geo = (node[3],node[4])
            strhnr = (node[0],node[1],node[2])
            print 'x=%-10.10s y=%-10.10s  %s %s%s' % (geo+strhnr),
            if not hold: print
        def printD(node,change,msg):
            reason = ['STR-HAUSNR','GEODATEN'][msg-1]
            if msg == 2:
                ch = 'x=%-10.10s y=%-10.10s' % (change[0],change[1])
            elif msg == 1:
                ch = '%s %s%s' % (change[0],change[1],change[2])
            printSimple(node,hold=True)
            print ch,reason
        if level in ['all']:
            print 'same in both'
            sB = self.sameInBoth
            for l in sB.keys():
                printSimple(sB[l])
##                for s in b:
##                    print '  ',s[0],s[1],s[2]
        if level in ['all','diff']:
            print 'different'
            sB = self.different
            for l in sB.keys():
                #print sB[l]
                printD(sB[l][0],sB[l][1],sB[l][2])
##                for s in b:
##                    if options.execute:
##                        p = os.popen('%s %s' % (options.execute, \
##                                    os.path.join(s[0],s[2])))
##                        print ' left',p.read(),
##                        p.close()
##                        p = os.popen('%s %s' % (options.execute, \
##                                    os.path.join(s[0].replace(self.leftPath, \
##                                                        self.rightPath),s[2])))
##                        print 'right',p.read(),
##                        p.close()
##                    else:
##                        print '  ',s[0],s[1],s[2]
        if 0 and level in ['all','diff','left']:
            print 'only in', self.leftPath
            sS = self.onlyInSelf
            for l in sS.keys():
                printSimple(sS[l])
                #print sS[l]
##                for s in b:
##                    print '  ',s[0],s[1],s[2]
        if level in ['all','diff','right']:
            print 'only in', self.rightPath
            sO = self.onlyInOther
            for l in sO.keys():
                printSimple(sO[l])
                #print sO[l]
##                for s in b:
##                    print '  ',s[0],s[1],s[2]
        return

    def cmpList(self,leftEntry,right,node):
        found = None
        hnr = leftEntry[1]
        for er in right.keys():
            rl = right[er]
            if hnr != rl[1]: continue
            if leftEntry[2] != rl[2]: continue
            if leftEntry[0] == rl[0]:
                found = rl
                break
        return found
    
    def dirDiff(self):
        left = self.leftList
        right = self.rightList
        self.onlyInSelf = {}
        self.onlyInOther = {}
        self.sameInBoth = {}
        self.different = {}
        log = []
        es = left.entries
        eo = right.entries
        for nodeSelf in es.keys():
            listsOther = eo.get(nodeSelf,None)
            if listsOther:
                log.append('comparing node %s' % str(nodeSelf))
                if es[nodeSelf] == eo[nodeSelf]:
                    self.sameInBoth[nodeSelf] = es[nodeSelf]
                else:
                    self.different[nodeSelf] = [es[nodeSelf],eo[nodeSelf][:3],1]
                del eo[nodeSelf]
            else:
                a = self.cmpList(es[nodeSelf],eo,nodeSelf)
                if a:
                    self.different[nodeSelf] = [es[nodeSelf],a[3:],2]
                    n = (a[3],a[4])
                    print nodeSelf
                    del eo[n]
                else:
                    self.onlyInSelf[nodeSelf] = es[nodeSelf]
                log.append('cmp node %s -- not exist in right' %
                           str(nodeSelf,))
        for nodeOther in eo.keys():
            self.onlyInOther[nodeOther] = eo[nodeOther]
            log.append('cmp node %s -- not exist in left' %
                       str(nodeOther,))
        return log

import stat,filecmp

class FileSystemElement:
    
    def __init__(self,path):
        self.path = path
        try:
            self.FSObject = os.stat(path)
        except:
            return
        self.mode = self.FSObject.st_mode
        self.name = os.path.split(path)[1]
        self.type = self.objectType(self.mode)
        
    def objectType(self,mode):
        objectTypes = ['d','f','o']
        typ = 'o'
        for e,t in enumerate([stat.S_ISDIR,stat.S_ISREG]):
            if t(mode):
                typ = objectTypes[e]
                break
        return typ

    def cmp(self,otherObject):
    # erster Ansatz:
    # directories by name
    # files by size
        isSame = self.name == otherObject.name and self.type == otherObject.type
        if not isSame:
            return isSame
        if stat.S_ISDIR(self.mode):
            isSame = True
        else:
            isSame = filecmp.cmp(self.path,otherObject.path,options.shallow)
            #print self.path,otherObject.path,isSame
##            if options.diff_date:
##                isSame = self.FSObject.st_mtime == otherObject.FSObject.st_mtime
##                #print self.path,self.FSObject.st_mtime,otherObject.FSObject.st_mtime,isSame
##            elif options.filecmp:
####                cmd = 'cmp %s %s' % (self.path,otherObject.path)
####                p = os.popen(cmd)
####                a = p.read()
####                isSame = not len(a)
####                print 'result',cmd,'#',len(a),isSame
####                p.close()
##            else:
##                isSame = self.FSObject.st_size == otherObject.FSObject.st_size
##                #print self.path,self.FSObject.st_size,otherObject.FSObject.st_size,isSame
        return isSame

class Liste:

    def __init__(self,root,filterList=None):
        self.path = root.rstrip('/')
        self.head,self.root = os.path.split(self.path)
        self.prefixLen = len(self.path) + 1   # +1, weil zwischen den Teilen des Pfads der PathSep ('/') steht
        self.filter = filterList
##        self.list = os.walk(root)
##        print '########'
##        for i in self.list:  #der generator müsste wieder auf "seek(0)" gestellt werden
##            print i[0]       # wie geht das???
        #print 'root in Liste()',root
        self.entries = self.readList(self.readFile(root))  # dict containing all entries of List
        if filterList:
            self.entries = self.applyFilter(self.entries)
        self.len = len(self.entries)
        return

    def shortPath(self,path):
        return path[self.prefixLen:]

    def getObject(self,node,liste,obj):
        o = self.entries[node][liste]
        idx = o.index(obj)
        path = os.path.join(self.path,node,o[idx])
        return FileSystemElement(path)
        
    def readList(self,liste):
        print 'reading',self.path
        e = {}
        for i in liste:
            if not i: continue
            f = i.split(';')
            koord = (f[-2],f[-1])
            e[koord] = f
            #print koord,f
        return e

    def readFile(self,fname):
        f = file(fname)
        r = f.read().decode('latin-1','replace').encode('utf-8','replace')
        #print r
        e = r.split('\n')
        return e

    def applyFilter(self, entries):
        # delete members of the internal list that equal any filter entry
        for i in entries.keys():
            e = entries[i]
            #print 'entry',e
            found = False
            for f in self.filter:
                if f in e[0]:
                    del entries[i]
                    found = True
                    break
            if found: continue
            for n in [1,2]:
                for m in e[n]:
                    for f in self.filter:
                        if f == m:
                            e[n].remove(m)
        return entries

    def printList(self, typeInfo=None):
        for e in self.entries.keys():
            i = self.entries[e]
            print e,i[0]
            for e,c in enumerate(['d','f']):
                if not typeInfo or (c in typeInfo):
                    print ' ',c,len(i[e+1]),i[e+1]
        return


def talk(msg):
    if options.verbose:
        print msg
    return

def main(left,right,options,commands):
    talk("""compare 2 directories: %s -> %s""" % (left,right))
    filterList = options.filter
    verbose = options.verbose
    lLeft  = Liste(left,filterList)
    lRight = Liste(right,filterList)
##    for i in [lLeft,lRight]:
##        print i.len,'#',i.path,'#',i.root
##        if 0 and verbose:
##            i.printList()
##    lLeft.printList() #typeInfo=('d'))
##    lRight.printList() #typeInfo=('d'))
    for c in commands:
        if c == 'file-diff':
            #log = lLeft.dirDiff(lRight)
            if verbose:
                lLeft.printDiff(level='all')
            else:
                lLeft.printDiff(level='diff')
        if c == 'dir-diff':
            diff = Diff(lLeft,lRight)
            log = diff.dirDiff()
            if options.details:
                for l in log:
                    print l
            if verbose:
                diff.printDiff(level='all')
            else:
                diff.printDiff(level='diff')
    return
    
if __name__ == "__main__":
    usage = """usage: %prog [options] command left-path right-path
    compare file-structures object by object.
    (other list-types will be supported in later versions)

commands:
  dir-diff              (default)

TODOs:
  -  -i  ignore case
  -  Ausgabe von 'node's untersuchen und evtl. abschalten."""
    parser = OptionParser(usage)
    parser.add_option("-f", "--filter", dest="filter",
                  metavar="<filter>", help="exclude these (comma separated list of) patterns ")
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    parser.add_option("-S", "--shallow",
                  action="store_false", dest="shallow", default=True,
                  help="switch off shallow comparison in filecmp")
    parser.add_option("-d", "--details",
                  action="store_true", dest="details", default=False,
                  help="print detailed information on comparisons")
##    parser.add_option("-d", "--date",
##                  action="store_true", dest="diff_date", default=False,
##                  help="compare filesystem objects by date (mtime) only")
    parser.add_option("-e", "--exec", dest="execute", 
                  default=False, metavar="<command>",
                  help="execute command for 'different' objects")

    (options, args) = parser.parse_args()
    if options.filter:
        options.filter = options.filter.split(',')
    (left, right) = (args[-2], args[-1])
    commands = args[:-2]
    if not commands:
        commands = ['dir-diff']
    if options.verbose:
        print "options",options
        print "args",args
        print "commands",commands
    #sys.exit(0)
    main(left,right,options,commands)
