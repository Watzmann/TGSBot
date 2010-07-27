#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Implementierung von User und User-related Routinen."""

class User:
    def __init__(self, name, pw):
        self.name = name
        self.password = pw
        print 'This is USER %s with pw %s' % (name, '*'*len(pw))
        
def getUser(**kw):
    return User(kw['user'], kw['password'])
