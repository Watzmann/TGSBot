#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Testing decorator syntax."""

def makebold(fn):
    def wrapped():
        print 'bold', fn, fn()
        return "<b>" + fn() + "</blu>"
    return wrapped

def makeitalic(fn):
    def wrapped():
        print 'italic', fn, fn()
        return "<i>" + fn() + "</ita>"
    return wrapped

@makebold
@makeitalic
def hello():
    return "hello world"

print '-'*60
print hello() ## returns <b><i>hello world</i></b>
print '-'*60
print hello() ## returns <b><i>hello world</i></b>
print '-'*60
