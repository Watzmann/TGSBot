#!/usr/bin/python
# -*- coding: utf-8 -*-
"""was macht das script"""

import sys
import datetime
from calender import Days
from time import strptime
import auslesen
from zeit_spiele import zeit_archiv

def dump_zeit_archiv(archiv):
    return

if __name__ == '__main__':
    args = len(sys.argv)
    fmt = '%d.%m.%Y'
    if args == 2:
        first_day = sys.argv[1]
        last_day = datetime.date.today().strftime(fmt)
    elif args == 3:
        first_day = sys.argv[1]
        last_day = sys.argv[2]
    else:
        first_day = datetime.date.today().strftime(fmt)
        last_day = datetime.date.today().strftime(fmt)
    #print first_day, last_day
    
    d1 = datetime.date(*strptime(first_day,fmt)[0:3])
    d2 = datetime.date(*strptime(last_day,fmt)[0:3])
    #print d1, d2

    for d in Days(d1,d2):
        #print >> sys.stderr, d
        for i in [2,3,4]:
            dump = auslesen.Sucher(d.year,d.month,d.day,i)
            label = dump.label
            if zeit_archiv.has_key(label):
                continue
            game = dump.game
            print >> sys.stderr, game
            dump.suche()
            zeit_archiv.update(dump.zs.entries())

##    zkeys = zeit_archiv.keys()
##    zkeys.sort()
##    for z in zkeys:
##        print z
