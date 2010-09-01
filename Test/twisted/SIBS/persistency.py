#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Persistenzschicht."""

REV = '$Revision$'

import shelve
from version import Version

v = Version()
v.register(__name__, REV)

class Db:
    # TODO:   es ist jetzt ein Singleton (Borg), aber folgendes Problem:
    #         natürlich will ich ein Singleton für die EINE DB (z.B. Users),
    #         aber natürlich will ich genauso ein weiteres Singleton für die
    #         nächste DB, z.B. Games. Es müssen von diesem Typ also mehrere
    #         Singletons bestehen :)

    __shared_state = {}     # Borg Pattern
                            # http://code.activestate.com/recipes/66531-singleton-we-dont-need-no-stinkin-singleton-the-bo/

    def __init__(self, db_name='shelve.db'):
        self.__dict__ = self.__shared_state
        if not hasattr(self, 'db_name'):
            self.db_name = db_name
            self.db = self._rawopen()
            self.open = True

    def _rawopen(self,):
        return shelve.open(self.db_name, writeback=True)
    
    def sync(self,):
        self.db.sync()

    def close(self,):
        self.db.close()
        self.open = False

    def reopen(self,):
        if not self.open:
            self.db = self._rawopen()
            self.open = True

class Persistent:
    def __init__(self, db_name='persistency.db'):
        self.db_key = str(id(self))
        self.db = Db(db_name)
        
    def save(self,):
        print 'persistency saving', self.db_load
        self.db.db[self.db_key] = self.db_load
        self.db.db.sync()

