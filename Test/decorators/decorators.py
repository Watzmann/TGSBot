#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Testing decorator syntax."""

import sys

def decorator(decoree):
    def decor(arg):
        print 'bin ich verzierung', arg
        return decoree(arg+1)-1
    return decor

def func(arg):
    return arg * arg

func = decorator(func)

def doit(arg):
    arg = int(arg)
    print 'argument', arg
    print 'func', func(arg)
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg = sys.argv[1]
    else:
        arg = 2
    doit(arg)
