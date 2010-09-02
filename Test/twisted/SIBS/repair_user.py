#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Reparaturen/Migrationen in der Users-DB."""

from persistency import Persistent, Db
from sibs_user import Info

def login_time(db, key, value):
    print key, value.passwd, value.rating, value.login, value.host
    value.login = int(value.login)
    print key, value.passwd, value.rating, value.login, value.host
    print

def messages(db, key, v):
    data = (v.login,v.host, v.name, v.passwd, v.rating, v.experience)            
    info = Info(data, v.toggles, v.settings, [])
    db[key] = info
    
def for_all_users(db, repair):
    keys = db.keys()
    for e,k in enumerate(keys):
        repair(db, k, db[k])
    db.sync()
    
if __name__ == '__main__':
    db = Db('db/users')
    #repair = login_time
    #repair = messages
    for_all_users(db.db, repair)
    db.close()
