#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Persistenzschicht."""

from persistency import Persistent, Db
from StringIO import StringIO

class Test(Persistent):
    def __init__(self, a, b, c):
        Persistent.__init__(self, 'db/test_users')
        self.a = a
        self.b = b
        self.c = c
        self.db_load = {'a':self.a,'b':self.b,'c':self.c,}
        
    def __str__(self,):
        out = StringIO()
        print >>out, 'a:', self.a
        print >>out, 'b:', self.b
        print >>out, 'c:', self.c
        return out.getvalue()

def add():  
    for i in ((2,1.23,'erst'), ('funny', 'zweit', 15), ('drei','ss','4')):
        a,b,c = i
        t = Test(a,b,c)
        t.save()

if __name__ == '__main__':
    #add()
    db = Db('db/test_users')
    print 'DB dump'
    keys = db.db.keys()
    keys.sort()
##    a = db.db[keys[5]]
##    a['a'] = 'neunzehn'
####    db.sync()
##    print a
    for e,k in enumerate(keys):
        print e,k,db.db[k]
    db.close()
