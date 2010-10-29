#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Persistenzschicht."""

REV = '$Revision$'

import shelve
from version import Version

v = Version()
v.register(__name__, REV)

class Db:
        # TODO: wegen Borg ist die Geschichte nicht Threadsave. Da muss
        #       vielleicht noch mal gehirnt werden. Lock-Mechanismus

    __shared_state = {}     # Borg Pattern
                            # http://code.activestate.com/recipes/66531-singleton-we-dont-need-no-stinkin-singleton-the-bo/

    def __init__(self, db_name='shelve.db', db='default'):
        if not db in self.__shared_state:
            self.__shared_state[db] = {}
        self.__dict__ = self.__shared_state[db]
        print 'DB:: initializing', db_name, 'as', db
        if not hasattr(self, 'db_name'):
            self.db_name = db_name
            self.db = self._rawopen()

    def _rawopen(self,):
        print 'DB:: opening', self.db_name
        open_db = shelve.open(self.db_name, writeback=True)
        self.open = True
        return open_db
    
    def sync(self,):
        print 'DB:: syncing', self.db_name
        self.db.sync()

    def close(self,):
        print 'DB:: closing', self.db_name
        self.db.close()
        self.open = False

    def reopen(self,):
        print 'DB:: reopening', self.db_name
        if not self.open:
            self.db = self._rawopen()

class Persistent:
    def __init__(self, db_name='persistency.db', db='default'):
        self.db_key = str(id(self))
        self.db = Db(db_name, db)
        
    def save(self,):
        print 'persistency saving', self.db_load, 'to', self.db_key
        self.db.db[self.db_key] = self.db_load
        self.db.sync()

