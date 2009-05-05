#!/usr/bin/python
# -*- coding: utf-8 -*-

print 'hier spricht', __file__, __name__

#import package
from package import *
#import package.hallo
#from package import hallo

tries = [(hallo.test1,'hallo.test1',{}),
##         (,,{}),
##         (,,{}),
##         (,,{}),
##         (,,{}),
##         (,,{}),
##         (,,{}),
         ]

def excert(fun, msg, **kw):
    print '+'*60
    print ' ', msg
    fun(**kw)

def main():
    print __file__,'in main() gelandet'
    for i in tries:
        if len(i) < 1:
            continue
        f,m,kw = i
        excert(f,m,**kw)
    return

if __name__ == '__main__':
    main()
