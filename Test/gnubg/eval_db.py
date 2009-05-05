#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
u"""liest die Shelve-Datenbank <DB> aus.
    Mit 'verbose' lassen sich die Datensätze ausgeben.

    DB:     Name der Datenbank [dbshelve]"""
#

import time
from read_shelve import load_summary

def rating(x, **kw):
    key = kw.get('key','fibs_rating_error')
    if kw and kw.has_key('games') and kw['games']:
        ret = []
        games = x['games']
        for g in games:
            ret.append(g['global'].get(key,[''])[0])
    else:
        ret = [x['match']['global'].get(key,[''])[0]]
    return ret

def mtime(x):
    return x['info']['match_time']

def stime(x):
    return int(time2sec(mtime(x)))    
    
def time2sec(t):
    if type(t) == type(''):
        t = (0,0,0,0,0)
    return time.mktime(t + (0,0,0,0))

str2float = lambda c: float(c.replace(',','.'))
braces2float = lambda c: str2float(c.split(' ')[0])
sort_tuple = lambda x,y: int((str2float(x[1]) - str2float(y[1]))*1000)
sort_braces = lambda x,y: int((braces2float(x[1]) - braces2float(y[1]))*1000)
sort_mtime = lambda x,y: int(time2sec(x[1])-time2sec(y[1]))
sort_stime = lambda x,y: x[1]-y[1]

sorting_functions = {
        'fibs_rating_error':(rating,sort_tuple),
        'global_rate':(rating,sort_braces),
        'time':(mtime,sort_mtime),
        'time_s':(stime,sort_stime),
        }

def sort_liste(liste, key, order='asc', games=False):
    extract,sort_fct = sorting_functions[key]
    ret = []
    for l in liste:
        summary = load_summary(l)
        smry = summary.compose_summary()
        val = extract(smry, **{'key':key,'games':games})
##        print val, l, len(val),type(val)
        z = zip([l]*len(val),val)
        ret += z
    ret = [r for r in ret if r[1] != '']
    ret.sort(sort_fct)
    ret = [r[0] for r in ret]
    return ret

