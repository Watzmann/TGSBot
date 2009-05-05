#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Dient dem Herumspielen mit den svn:keywords"""

# $Date: 2006-09-20 16:25:39 +0200 (Mi, 20 Sep 2006) $
# $Revision: 40 $
# $Author: hausmann $
# $URL: svn://jupiter/Entwicklung/Python/trunk/Test/ah.py $
# $Id: ah.py 40 2006-09-20 14:28:20Z hausmann $

import os

# ~/tmp/ah1 erhält man durch folgenden find-Befehl auf /var/opt/zope/~/Products
# >find -name '*.py'|grep -v tests|xargs grep '\$.*\$'>~/tmp/ah1

f = file(os.path.expanduser('~/tmp/ah1'))
lines = [l.strip('\n') for l in f.readlines()]

liste = []
collect = {}

for l in lines: #[:20]:
    a = l.split('$')
    try:
        res = a[1].split(':')
        res = res[0]
        collect[res] = a[0]
    except:
        res = ''
    liste.append((a[0],res))

##for l in liste:
##    print l[1],'  ##  ',l[0]

for k in collect.keys():
    print k,'  ##  ',collect[k]
    
