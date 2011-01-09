#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Reparaturen/Migrationen in der Users-DB."""

from persistency import Persistent, Db
from sibs_user import Info
from time import time
import types

logout = int(time())

def data(v):
    return (v.login, v.last_logout, v.host, v.name, v.passwd, v.rating,
            v.experience, v.address)

def ndata(v):
    return (v.login, logout, v.host, v.name, v.passwd, v.rating,
            v.experience, '-')

def login_time(db, key, value):
    print key, value.passwd, value.rating, value.login, value.host
    value.login = int(value.login)
    print key, value.passwd, value.rating, value.login, value.host
    print

def logout_time(db, key, value):
    mydata = ndata(value)
    info = Info(mydata, value.toggles, value.settings, value.messages)
##    info.show()
    db[key] = info

def messages(db, key, value):
    vdata = data(value)
    info = Info(vdata, value.toggles, value.settings, value.messages,
                value.saved_games, [], [])
    db[key] = info
    
def special(db, key, value):
    vdata = data(value)
    saved_games = getattr(value, 'saved_games', {})
    if type(saved_games) is types.ListType:
        saved_games = {}
    gagged = getattr(value, 'gagged', [])
    blinded = getattr(value, 'blinded', [])
    special = getattr(value, 'special', '')
    info = Info(vdata, value.toggles, value.settings, value.messages,
                saved_games, gagged, blinded, special)
    db[key] = info
    
def saved(db, key, value):
    vdata = data(value)
    special = getattr(value, 'special', '')
    info = Info(vdata, value.toggles, value.settings, value.messages,
                {}, [], [], special)
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
    
def lower_keys(db,):
    keys = db.keys()
    for k in keys:
        l = k.lower()
        if l == k:
            continue
        if l in keys:
            print 'ERROR lower in keys', l, k
            del db[k]
        entry = db.get(k, db.get(k.lower(), None))
        if entry is None:
            print 'Warning: problems with %s (%s)' % (k,l)
        else:
            db[l] = entry
            del entry
    db.sync()
    
if __name__ == '__main__':
    db = Db('db/users')
    #repair = login_time
    #repair = messages
    #repair = special
    #repair = saved
    #repair = autoroll
    #repair = logout_time
    #for_all_users(db.db, repair)
    lower_keys(db.db)
    db.close()
