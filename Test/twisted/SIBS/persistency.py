#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Persistenzschicht."""

REV = '$Revision$'

import os
import shelve
import logging
from version import Version

v = Version()
v.register(__name__, REV)

TRACE = 15
logging.addLevelName(TRACE, 'TRACE')
logging.basicConfig(level=logging.INFO,
                format='%(name)s %(levelname)s %(message)s',
                )
logger = logging.getLogger('persistency')

class Db:
        # TODO: wegen Borg ist die Geschichte nicht Threadsave. Da muss
        #       vielleicht noch mal gehirnt werden. Lock-Mechanismus
        #
        #       NICHT THREADSAVE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!11
        #

    __shared_state = {}     # Borg Pattern
                            # http://code.activestate.com/recipes/66531-singleton-we-dont-need-no-stinkin-singleton-the-bo/

    def __init__(self, db_name='shelve.db', db='default'):
        if not db in self.__shared_state:
            self.__shared_state[db] = {'database': db}
        self.__dict__ = self.__shared_state[db]
        logger.info('DB:: initializing %s as %s' % (db_name, db))
        if not hasattr(self, 'db_name'):
            self.db_name = db_name
            self.db = self._rawopen()

    def get_db(self,):
        return self.db

    def _rawopen(self,):
        logger.info('DB:: opening %s' % self.db_name)
        open_db = shelve.open(self.db_name, writeback=True)
        self.open = True
        return open_db
    
    def sync(self,):
        logger.info('DB:: syncing %s' % self.db_name)
        self.db.sync()

    def close(self,):
        logger.info('DB:: closing %s' % self.db_name)
        self.db.close()
        self.open = False

    def delete(self,):
        del self.__shared_state[self.database]

    def reopen(self,):
        logger.info('DB:: reopening %s' % self.db_name)
        if not self.open:
            self.db = self._rawopen()

    def pack(self,):
        packed_db_name = '.'.join((self.db_name,'packed'))
        old_db_name = '.'.join((self.db_name,'old'))
        db = Db(packed_db_name, 'packing')
        for k,v in self.db.items():
            print k,v
            db.db[k] = v
        db.close()
        db.delete()
        self.close()
        os.rename(self.db_name, old_db_name)
        os.rename(packed_db_name, self.db_name)
        self.reopen()
        self.rereference()

class Persistent:
    def __init__(self, db_name='persistency.db', db='default'):
        self.db_key = str(id(self))
        self.db = Db(db_name, db)
        
    def save(self, log=''):
        logger.info('saving (%s) %s to %s' % (log, self.db_load, self.db_key))
        self.db.db[self.db_key] = self.db_load
        self.db.sync()

    def delete(self,):
        logger.info('deleting %s' % self.db_key)
        del self.db.db[self.db_key]
        self.db.sync()
