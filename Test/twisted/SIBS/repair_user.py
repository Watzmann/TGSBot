#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Reparaturen/Migrationen in der Users-DB."""

from persistency import Persistent, Db

def login_time(key, value):
    print key, value.passwd, value.rating, value.login, value.host
    value.login = int(value.login)
    print key, value.passwd, value.rating, value.login, value.host
    print
    
def for_all_users(db, repair):
    keys = db.keys()
    for e,k in enumerate(keys):
        repair(k, db[k])
    db.sync()
    
if __name__ == '__main__':
    db = Db('db/users')
    #repair = login_time
    for_all_users(db.db, repair)
    db.close()
