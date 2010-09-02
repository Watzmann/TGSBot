#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Persistenzschicht."""

from persistency import Persistent, Db

if __name__ == '__main__':
    db = Db('db/users')
    keys = db.db.keys()
    keys.sort()
    print 'Registered users'
    for e,k in enumerate(keys):
        print e,k
    print 'Users entries'
##    print '   ',db.db.values()[0].toggles.keys()
    for e,k in enumerate(keys):
        print e,k
        v = db.db[k]
        print '   ', v.login, v.host, v.name, v.passwd, v.rating, v.experience,
##        print '   ',v.toggles.values()
        print '   ',v.settings
##        print '   ',v.messages
    db.close()
