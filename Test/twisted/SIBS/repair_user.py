#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Reparaturen/Migrationen in der Users-DB."""

from persistency import Persistent, Db
from sibs_user import Info

def data(v):
    return (v.login, v.host, v.name, v.passwd, v.rating, v.experience)            

def login_time(db, key, value):
    print key, value.passwd, value.rating, value.login, value.host
    value.login = int(value.login)
    print key, value.passwd, value.rating, value.login, value.host
    print

def messages(db, key, value):
    vdata = data(value)
    info = Info(vdata, v.toggles, v.settings, [])
    db[key] = info
    
def autoroll(db, key, value):
    vdata = data(value)
    toggles = value.toggles
    if (not 'autoroll' in toggles) and ('double' in toggles):
        toggles['autoroll'] = not toggles['double']
    info = Info(vdata, toggles, value.settings, value.messages)
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
    #repair = autoroll
    for_all_users(db.db, repair)
    db.close()
