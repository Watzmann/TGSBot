#!/usr/bin/python
# -*- coding: utf-8 -*-
"""vergleicht Verzeichnisse und auch individuelle File-Objekte

(c) 10/2005 Andreas Hausmann
"""
__TODO__ = u"""
  -  -i  ignore case
  -  -M  Vergleich auf den Datei-Modus beziehen (chmod)
  -  -U  Vergleich auf den Datei-Besitz beziehen (user/group)
  -  -s  Statistik: Zahl der Einträge in jedem Teil der Liste
  -  Ausgabe von 'node's untersuchen und evtl. abschalten."""

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
        def printLine(line):
            path,flag,leaf = line
            print '  ',flag,os.path.join(path,leaf)

        if level in ['all']: # and len(self.sameInBoth):
            print 'same in both'
            sB = self.sameInBoth
            for l in sB.keys():
                b = sB[l]
                for s in b:
                    printLine(s)
        if level in ['all','diff']: # and len(self.different):
            print 'different' #,len(self.different)
            sB = self.different
            #print sB
            for l in sB.keys():
                b = sB[l]
                #print b
                for s in b:
                    if options.execute:
                        p = os.popen('%s %s' % (options.execute, \
                                    os.path.join(s[0],s[2])))
                        print ' left',p.read(),
                        p.close()
                        p = os.popen('%s %s' % (options.execute, \
                                    os.path.join(s[0].replace(self.leftPath, \
                                                        self.rightPath),s[2])))
                        print 'right',p.read(),
                        p.close()
                    else:
                        printLine(s)
        if level in ['all','diff','left']: # and len(self.onlyInSelf):
            print 'only in', self.leftPath #,len(self.onlyInSelf)
            sS = self.onlyInSelf
            for l in sS.keys():
                b = sS[l]
                #print '###',b
                for s in b:
                    if s[1] == 'node':
                        continue
                    printLine(s)
        if level in ['all','diff','right']: # and len(self.onlyInOther):
            print 'only in', self.rightPath
            sO = self.onlyInOther
            for l in sO.keys():
                b = sO[l]
                for s in b:
                    if s[1] == 'node':
                        continue
                    printLine(s)
        return

    def cmpList(self,left,right,node,lst):
        onlyMe = []
        same = []
        different = []
        for i in left[node][lst]:
            if i in right[node][lst]:
                lO = self.leftList.getObject(node,lst,i)
                rO = self.rightList.getObject(node,lst,i)
                right[node][lst].remove(i)
                isSame = None
                try:
                    isSame = lO.cmp(rO)
                except AttributeError:
                    isSame = True
                if isSame:
                    same.append(i)
                else:
                    different.append(i)
            else:
                onlyMe.append(i)
        return (onlyMe,right[node][lst],same,different)
    
    def dirDiff(self):
    
        def evalList(objType):
            objects = {'d':'directories','f':'files'}
            if os or oo or s or d:
                log.append('  comparing %s:' % objects[objType])
            for l,e,f,t in zip([s,d,os,oo],[es,es,es,eo], \
                                        [self.sameInBoth,self.different,self.onlyInSelf,self.onlyInOther], \
                                        ['  same objects:','  different objects:','  only left:','  only right:']):
                if l:
                    log.append(t)
                for o in l:
                    f[nodeSelf].append((e[nodeSelf][0],objType,o))
                    log.append('    %s' % o)
            return
        
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
                log.append('comparing node %s' % nodeSelf)
                self.sameInBoth[nodeSelf] = []
                self.different[nodeSelf] = []
                self.onlyInSelf[nodeSelf] = []
                self.onlyInOther[nodeSelf] = []
                os,oo,s,d = self.cmpList(es,eo,nodeSelf,1)
                evalList('d')
                os,oo,s,d = self.cmpList(es,eo,nodeSelf,2)
                evalList('f')
                del eo[nodeSelf]
            else:
                self.onlyInSelf[nodeSelf] = [(nodeSelf,'node','')]
                log.append('cmp node %s -- not exist in right' %
                           (nodeSelf,))
        for nodeOther in eo.keys():
            self.onlyInOther[nodeOther] = [(nodeOther,'node','')]
            log.append('cmp node %s -- not exist in left' %
                       (nodeOther,))
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
        self._trace = "Liste:: %s"
        self.path = root.rstrip('/')
        talk(self._trace % ("self.path: %s" % self.path), True)
        self.head,self.root = os.path.split(self.path)
        talk(self._trace % ("self.head: %s" % self.head), True)
        talk(self._trace % ("self.root: %s" % self.root), True)
        self.prefixLen = len(self.path) + 1   # +1, weil zwischen den Teilen des Pfads der PathSep ('/') steht
        talk(self._trace % ("self.prefixLen: %s" % self.prefixLen), True)
        self.filter = filterList
##        self.list = os.walk(root)
##        print '########'
##        for i in self.list:  #der generator müsste wieder auf "seek(0)" gestellt werden
##            print i[0]       # wie geht das???
        self.entries = self.readList(os.walk(root))  # dict containing all entries of walk
        if filterList is not None:
            talk(self._trace % ("self.filterList: %s" % self.filter), True)
            self.entries = self.applyFilter(self.entries)
        self.len = len(self.entries)
        talk(self._trace % ("self.len: %s" % self.len), True)        
        return

    def shortPath(self,path):
        return path[self.prefixLen:]

    def getObject(self,node,liste,obj):
        o = self.entries[node][liste]
        idx = o.index(obj)
        path = os.path.join(self.path,node,o[idx])
        return FileSystemElement(path)
        
    def readList(self,liste):
        e = {}
        for i in liste:
            sp = self.shortPath(i[0])
            e[sp] = i
        return e

    def applyFilter(self, entries):
        # delete members of the internal list that equal any filter entry
        #print self.filter
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
                for m in e[n][:]:
                    for f in self.filter:
                        #print '++',f,m,
                        if f == m or f in m:
                            e[n].remove(m)
    ##                        print 'removed'
    ##                        break
    ##                    else:
    ##                        print
        return entries

    def printList(self, typeInfo=None):
        for e in self.entries.keys():
            i = self.entries[e]
            print e,i[0]
            for e,c in enumerate(['d','f']):
                if not typeInfo or (c in typeInfo):
                    print ' ',c,len(i[e+1]),i[e+1]
        return


def talk(msg, _trace=False):
    if options.verbose:
        print msg
    if options.trace and _trace:
        print 'TRACE:',msg
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

TODOs:""" + __TODO__
    parser = OptionParser(usage)
    parser.add_option("-f", "--filter", dest="filter",
                  metavar="<filter>", help="exclude these (comma separated list of) patterns ")
    parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="print status messages to stdout")
    parser.add_option("-t", "--trace",
                  action="store_true", dest="trace", default=False,
                  help="print trace information to stdout")
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
