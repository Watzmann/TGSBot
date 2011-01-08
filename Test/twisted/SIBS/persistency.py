#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Persistenzschicht."""

REV = '$Revision$'

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

    __shared_state = {}     # Borg Pattern
                            # http://code.activestate.com/recipes/66531-singleton-we-dont-need-no-stinkin-singleton-the-bo/

    def __init__(self, db_name='shelve.db', db='default'):
        if not db in self.__shared_state:
            self.__shared_state[db] = {}
        self.__dict__ = self.__shared_state[db]
        logger.info('DB:: initializing %s as %s' % (db_name, db))
        if not hasattr(self, 'db_name'):
            self.db_name = db_name
            self.db = self._rawopen()

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

    def reopen(self,):
        logger.info('DB:: reopening %s' % self.db_name)
        if not self.open:
            self.db = self._rawopen()

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
