#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Persistenzschicht."""

import shelve
from StringIO import StringIO

class Db:       # TODO: die Geschichte mit dem Singleton

    __shared_state = {}

    def __init__(self, db_name=''):
        self.__dict__ = self.__shared_state
        if not hasattr(self, 'db_name'):
            self.db_name = db_name
            self.db = shelve.open(db_name)

    def sync(self,):
        self.db.sync()

    def close(self,):
        self.db.close()

class Persistent:
    def __init__(self,):
        self.db_key = str(id(self))
        self.db = Db('db/test_users')
        
    def save(self,):
        self.db.db[self.db_key] = self.db_load
        self.db.db.sync()

class Test(Persistent):
    def __init__(self, a, b, c):
        Persistent.__init__(self)
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
        
if __name__ == '__main__':
    test = {}
    for i in ((2,1.23,'erst'), ('funny', 'zweit', 15), ('drei','ss','4')):
        a,b,c = i
        test[i] = Test(a,b,c)
        test[i].save()
    db = Db()
    print 'DB dump'
    for e,k in enumerate(db.db.keys()):
        print e,k,db.db[k]
    db.close()
