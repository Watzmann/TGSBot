#!/usr/bin/python

print __name__,'in',__file__

#import sys, os

##for s in sys.path:
##    print s

class B:
    "bin isch glass B oder was?"
    lfdNr = 0
    def __init__(self):
        pass
    def getLfdNr(self):
        self.lfdNr += 1
        return self.lfdNr
    def eins(self):
        print 'eins:',self.getLfdNr(),self.lfdNr
        #self.lfdNr += 1
    def zwei(self):
        print 'zwei:',self.getLfdNr(),self.lfdNr
        #self.lfdNr += 1

def main():
    "warum soll man sich gegen die alten Gewohnheiten stellen?"
    print 'Klasse:',B.lfdNr
    a = B()
    for i in range(10):
        a.eins()
    for i in range(10):
        a.zwei()
    b = B()
    b.eins()
    a.eins()
    b.eins()
    a.eins()
    print 'Klasse:',B.lfdNr
    print B.__doc__
    print b.__doc__
    return

if __name__ == '__main__':
    print main.__doc__
    main()
