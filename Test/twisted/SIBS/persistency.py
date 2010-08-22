#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Persistenzschicht."""

import shelve

class Db:       # TODO: die Geschichte mit dem Singleton

    __shared_state = {}

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
        self.db.db[self.db_key] = self.db_load
        self.db.db.sync()

